# -*- coding: utf-8 -*-
"""make_bg + 네트워크/콘솔 계측 + 정지시 page.reload() 복구 시도. 세션노화 근본원인 진단용.
사용: python make_bg_diag.py --img X --prompt-file P --out O"""
import sys, os, time, argparse, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")

API_LOG = []       # (t, method, urltail, status)
CONSOLE_ERR = []


def click_text(page, text, exact=False):
    js = """(a)=>{const [t,ex]=a;const els=[...document.querySelectorAll('button,[role=button],[role=menuitem],div,span,a,li')];
      let best=null,ba=1e9;for(const e of els){const s=(e.innerText||e.textContent||'').trim();
      if(!s)continue;if(ex?s!==t:!s.includes(t))continue;if(s.length>60)continue;
      const r=e.getBoundingClientRect();if(r.width<6||r.height<6||r.top<0)continue;const ar=r.width*r.height;
      if(ar<ba){ba=ar;best={x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}}return best;}"""
    pos = page.evaluate(js, [text, exact])
    if pos: page.mouse.click(pos['x'], pos['y'])
    return pos


def vids(page):
    return page.evaluate("""()=>[...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src).filter(s=>s&&s.length>20)""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--prompt-file", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    img = os.path.abspath(a.img)
    txt = open(a.prompt_file, encoding="utf-8").read()
    m = re.search(r'(?m)^((?:2D|Clean|Inside|Looking|A |The )[^\n]{60,})$', txt)
    prompt = m.group(1).strip() if m else txt.strip().splitlines()[-1]

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        page = next((x for x in ctx.pages if "flow/project" in x.url), None)
        page.bring_to_front(); time.sleep(1.5)

        t0 = time.time()
        def on_resp(r):
            u = r.url
            if "labs.google" in u and ("/api/" in u or "trpc" in u):
                tail = u.split("labs.google")[-1][:80]
                if r.request.method == "POST" or r.status >= 400 or "generate" in u.lower():
                    API_LOG.append((round(time.time()-t0,1), r.request.method, tail, r.status))
        page.on("response", on_resp)
        page.on("console", lambda msg: CONSOLE_ERR.append((round(time.time()-t0,1), msg.type, msg.text[:120])) if msg.type in ("error",) else None)

        before = set(vids(page))
        inp = page.query_selector_all("input[type=file]"); inp[0].set_input_files(img); print("uploaded"); time.sleep(9)
        tiles = page.evaluate("""()=>[...document.querySelectorAll('img')].filter(e=>{const r=e.getBoundingClientRect();return r.width>140&&r.top<innerHeight*0.6;}).map(e=>{const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),w:Math.round(r.width),h:Math.round(r.height),ar:r.width/r.height};})""")
        land = [t for t in tiles if t['ar'] > 1.3]; tg = land[0]
        page.mouse.move(tg['x'], tg['y']); time.sleep(1.2)
        page.mouse.click(tg['x']+tg['w']//2-28, tg['y']-tg['h']//2+28); time.sleep(1.0)
        click_text(page, "애니메이션 적용"); time.sleep(2.0)
        chip = page.evaluate("""()=>{const e=[...document.querySelectorAll('button')].find(b=>/8s/.test(b.innerText||''));const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}""")
        page.mouse.click(chip['x'], chip['y']); time.sleep(1.0)
        click_text(page, "1x", exact=True); time.sleep(0.3)
        click_text(page, "16:9", exact=True); time.sleep(0.3)
        click_text(page, "8s", exact=True); time.sleep(0.3)
        page.keyboard.press("Escape"); time.sleep(0.5)
        ed = page.evaluate("""()=>{const e=document.querySelector('[contenteditable=true],[role=textbox]');const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};}""")
        page.mouse.click(ed['x'], ed['y']); time.sleep(0.4)
        page.keyboard.type(prompt, delay=1); time.sleep(0.6)
        print("=== SEND ===")
        API_LOG.append(("SEND", "", "", ""))
        click_text(page, "arrow_forward"); time.sleep(3)

        got = None; reloaded = False
        for i in range(50):
            time.sleep(5)
            cur = [s for s in vids(page) if s not in before]
            body = page.evaluate("document.body.innerText")
            mm = re.search(r'(\d+)%', body); pct = mm.group(1) if mm else '?'
            print(f"[{(i+1)*5}s] newvid={len(cur)} pct={pct}")
            if cur: got = cur[0]; break
            # 정지 감지: 45초까지 pct 진전 없으면 reload 복구 시도 1회
            if not reloaded and (i+1)*5 >= 45 and pct == '?':
                print(">>> STALL detected → page.reload() 복구 시도")
                page.reload(wait_until="domcontentloaded"); time.sleep(8); reloaded = True
        if got:
            open(a.out, "wb").write(ctx.request.get(got).body()); print("DOWNLOADED", a.out)
        else:
            print("NO VIDEO")
        print("\n=== API_LOG (labs.google api: 오류/generate/media) ===")
        for row in API_LOG: print(row)
        print("=== CONSOLE ERRORS ===")
        for row in CONSOLE_ERR[-15:]: print(row)


if __name__ == "__main__":
    main()
