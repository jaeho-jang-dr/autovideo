# -*- coding: utf-8 -*-
"""이미 업로드된 배경 타일에 '애니메이션 적용'(첫프레임=이미지, 규격 자동일치) → 프롬프트 → 대기 → 다운로드.
사용: python make_bg_anim.py --prompt-file W22/bg/vprompt_elevator_up_v2.txt --out W22/bg/vid_elevator_up_v2.mp4 [--tile-ar 1.6]"""
import sys, os, time, argparse, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")


def click_text(page, text, exact=False):
    js = """(args)=>{const [t,exact]=args;
      const els=[...document.querySelectorAll('button,[role=button],[role=menuitem],div,span,a,li')];
      let best=null,ba=1e9;
      for(const e of els){const s=(e.innerText||e.textContent||'').trim();
        if(!s) continue; if(exact? s!==t : !s.includes(t)) continue; if(s.length>60) continue;
        const r=e.getBoundingClientRect(); if(r.width<6||r.height<6||r.top<0) continue; const a=r.width*r.height;
        if(a<ba){ba=a;best={x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}}
      return best;}"""
    pos = page.evaluate(js, [text, exact])
    if pos:
        page.mouse.click(pos['x'], pos['y'])
    return pos


def vids(page):
    return page.evaluate("""()=>[...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src).filter(s=>s&&s.length>20)""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tile-ar", type=float, default=1.3)
    a = ap.parse_args()
    txt = open(a.prompt_file, encoding="utf-8").read()
    m = re.search(r'(?m)^((?:2D|Clean|Inside|Looking|A |The )[^\n]{60,})$', txt)
    prompt = m.group(1).strip() if m else txt.strip().splitlines()[-1]
    print("PROMPT:", prompt[:70], "...")

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        page = next((x for x in ctx.pages if "flow/project" in x.url), None)
        page.bring_to_front(); time.sleep(1)
        before = set(vids(page))

        # find landscape tile (uploaded bg)
        tiles = page.evaluate("""()=>[...document.querySelectorAll('img')].filter(e=>{const r=e.getBoundingClientRect();return r.width>140&&r.top<innerHeight*0.6;}).map(e=>{const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),w:Math.round(r.width),h:Math.round(r.height),ar:r.width/r.height};})""")
        land = [t for t in tiles if t['ar'] > a.tile_ar]
        if not land:
            print("NO landscape tile"); return
        tg = land[0]
        print("tile", tg)
        page.mouse.move(tg['x'], tg['y']); time.sleep(1.2)
        mvx = tg['x'] + tg['w']//2 - 28; mvy = tg['y'] - tg['h']//2 + 28
        page.mouse.click(mvx, mvy); time.sleep(1.0)  # tile ⋮
        page.screenshot(path="scratch/flow/bga_menu.png")
        ok = click_text(page, "애니메이션 적용")
        print("애니메이션적용", ok); time.sleep(2.0)
        page.screenshot(path="scratch/flow/bga_anim.png")

        # type prompt into composer
        ed = page.evaluate("""()=>{const e=document.querySelector('[contenteditable=true],[role=textbox]');if(!e)return null;const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}""")
        if ed:
            page.mouse.click(ed['x'], ed['y']); time.sleep(0.4)
            page.keyboard.type(prompt, delay=1); time.sleep(0.6)
        # verify chip aspect
        chip = page.evaluate("""()=>{const b=[...document.querySelectorAll('button')].find(e=>/8s/.test(e.innerText||''));return b?b.innerText.replace(/\\s+/g,' '):null;}""")
        print("chip:", chip)
        page.screenshot(path="scratch/flow/bga_typed.png")
        click_text(page, "arrow_forward"); time.sleep(3)
        page.screenshot(path="scratch/flow/bga_sent.png")

        got = None
        for i in range(45):
            time.sleep(5)
            cur = [s for s in vids(page) if s not in before]
            body = page.evaluate("document.body.innerText")
            mm = re.search(r'(\d+)%', body); pct = mm.group(1) if mm else '?'
            print(f"[{(i+1)*5}s] newvid={len(cur)} pct={pct}")
            if cur:
                got = cur[0]; break
        print("SRC", got[:60] if got else None)
        if got:
            data = ctx.request.get(got).body()
            open(a.out, "wb").write(data)
            print("DOWNLOADED", a.out, len(data), "bytes")
        page.screenshot(path="scratch/flow/bga_final.png")


if __name__ == "__main__":
    main()
