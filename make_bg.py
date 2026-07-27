# -*- coding: utf-8 -*-
"""Flow 배경 동영상 1개: 업로드→애니메이션적용→16:9·8s·Veo3.1Lite 확인→프롬프트→대기→다운로드.
사용: python make_bg.py --img W22/bg/x.png --prompt-file P.txt --out W22/bg/x.mp4"""
import sys, os, time, argparse, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PROJ_URL = "https://labs.google/fx/ko/tools/flow/project/169bc73b-f8c6-46e5-ba61-e67e729c90d4"


def click_text(page, text, exact=False):
    js = """(a)=>{const [t,ex]=a;const els=[...document.querySelectorAll('button,[role=button],[role=menuitem],div,span,a,li')];
      let best=null,ba=1e9;for(const e of els){const s=(e.innerText||e.textContent||'').trim();
      if(!s)continue;if(ex?s!==t:!s.includes(t))continue;if(s.length>60)continue;
      const r=e.getBoundingClientRect();if(r.width<6||r.height<6||r.top<0)continue;const ar=r.width*r.height;
      if(ar<ba){ba=ar;best={x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}}return best;}"""
    pos = page.evaluate(js, [text, exact])
    if pos:
        page.mouse.click(pos['x'], pos['y'])
    return pos


def vids(page):
    return page.evaluate("""()=>[...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src).filter(s=>s&&s.length>20)""")


def media_names(page):
    return set(page.evaluate("""()=>[...document.querySelectorAll('img')].map(e=>{const m=(e.currentSrc||e.src||'').match(/name=([0-9a-f-]{20,})/);return m?m[1]:null;}).filter(Boolean)"""))


def new_video_tiles(page, before):
    # 새로 생긴 가로형 동영상 타일(play_circle) 이름, 위→아래·좌→우
    js = """(before)=>{const out=[];document.querySelectorAll('img').forEach(im=>{const r=im.getBoundingClientRect();if(r.width<140||r.top>innerHeight*0.6)return;const m=(im.currentSrc||im.src||'').match(/name=([0-9a-f-]{20,})/);if(!m)return;if(before.includes(m[1]))return;if(r.width/r.height<1.3)return;let el=im,play=false;for(let k=0;k<5&&el;k++){if(/play_circle|play_arrow/.test(el.innerText||'')){play=true;break;}el=el.parentElement;}if(!play)return;out.push({name:m[1],y:Math.round(r.top),x:Math.round(r.left)});});out.sort((a,b)=>a.y-b.y||a.x-b.x);return out;}"""
    return page.evaluate(js, list(before))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    img = os.path.abspath(a.img); base = os.path.basename(img)
    txt = open(a.prompt_file, encoding="utf-8").read()
    m = re.search(r'(?m)^((?:2D|Clean|Inside|Looking|A |The )[^\n]{60,})$', txt)
    prompt = m.group(1).strip() if m else txt.strip().splitlines()[-1]
    print("IMG", base, "| PROMPT", prompt[:60], "...")

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        page = next((x for x in ctx.pages if "flow/project" in x.url), None)
        if not page:
            page = ctx.pages[0]; page.goto(PROJ_URL, wait_until="domcontentloaded"); time.sleep(6)
        page.bring_to_front(); time.sleep(1.5)
        before = set(vids(page))

        # 1) upload
        inp = page.query_selector_all("input[type=file]")
        inp[0].set_input_files(img); print("uploaded"); time.sleep(9)

        # 2) find landscape tile, tile ⋮, 애니메이션 적용
        tiles = page.evaluate("""()=>[...document.querySelectorAll('img')].filter(e=>{const r=e.getBoundingClientRect();return r.width>140&&r.top<innerHeight*0.6;}).map(e=>{const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),w:Math.round(r.width),h:Math.round(r.height),ar:r.width/r.height};})""")
        land = [t for t in tiles if t['ar'] > 1.3]
        if not land:
            print("NO landscape tile", tiles); return
        tg = land[0]; print("tile", tg)
        page.mouse.move(tg['x'], tg['y']); time.sleep(1.2)
        page.mouse.click(tg['x']+tg['w']//2-28, tg['y']-tg['h']//2+28); time.sleep(1.0)  # tile ⋮
        anim = click_text(page, "애니메이션 적용"); print("애니메이션적용", bool(anim)); time.sleep(2.0)

        # 3) open model menu, ensure 16:9 + 8s, verify Veo 3.1 Lite
        chip = page.evaluate("""()=>{const e=[...document.querySelectorAll('button')].find(b=>/8s/.test(b.innerText||''));if(!e)return null;const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}""")
        if chip:
            page.mouse.click(chip['x'], chip['y']); time.sleep(1.0)
            menu = page.evaluate("document.body.innerText")
            model_ok = "Veo 3.1 - Lite" in menu
            print("model Veo3.1Lite:", model_ok)
            click_text(page, "1x", exact=True); time.sleep(0.4)   # 수량 1개(x3 낭비 방지)
            click_text(page, "16:9", exact=True); time.sleep(0.4)
            click_text(page, "8s", exact=True); time.sleep(0.4)
            page.keyboard.press("Escape"); time.sleep(0.6)

        # 4) type prompt + send
        ed = page.evaluate("""()=>{const e=document.querySelector('[contenteditable=true],[role=textbox]');if(!e)return null;const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}""")
        page.mouse.click(ed['x'], ed['y']); time.sleep(0.4)
        page.keyboard.press("Control+A"); page.keyboard.press("Delete"); time.sleep(0.2)
        page.keyboard.insert_text(prompt); time.sleep(0.8)   # ★한번에 삽입(keyboard.type는 무거운페이지서 키누락→프롬프트불완전→send비활성)
        chiptxt = page.evaluate("""()=>{const b=[...document.querySelectorAll('button')].find(e=>/8s/.test(e.innerText||''));return b?b.innerText.replace(/\\s+/g,' '):'';}""")
        print("chip:", chiptxt)
        before_names = media_names(page)   # send 직전 미디어 이름
        click_text(page, "arrow_forward"); time.sleep(3)

        # 5) wait + download (새 동영상 타일 이름 차집합으로 정확히 잡기)
        got_name = None
        for i in range(60):
            time.sleep(5)
            nt = new_video_tiles(page, before_names)
            body = page.evaluate("document.body.innerText")
            mm = re.search(r'(\d+)%', body); pct = mm.group(1) if mm else '?'
            print(f"[{(i+1)*5}s] newtiles={len(nt)} pct={pct}")
            if nt:
                got_name = nt[0]['name']; break
        if got_name:
            url = f"https://labs.google/fx/api/trpc/media.getMediaUrlRedirect?name={got_name}"
            data = ctx.request.get(url).body(); open(a.out, "wb").write(data)
            print("DOWNLOADED", a.out, len(data), "bytes from", got_name)
        else:
            print("NO VIDEO")
        page.screenshot(path="scratch/flow/mkbg_final.png")


if __name__ == "__main__":
    main()
