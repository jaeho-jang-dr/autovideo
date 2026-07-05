# -*- coding: utf-8 -*-
"""CDP 대화형 제어 헬퍼 — 살아있는 크롬(9222)에 붙어 한 동작 실행 + 스샷.
사용:
  python cdp.py goto <url>
  python cdp.py shot [name]
  python cdp.py click "<text>"            # 텍스트로 클릭
  python cdp.py clickxy <x> <y>
  python cdp.py rowcell "<lang>" "<col>"  # 언어행×열 셀 좌표 클릭 (자막/제목 및 설명)
  python cdp.py setfile <path>            # 모든 #captions-file-loader 에 파일 지정
  python cdp.py role button "<name>"      # 역할+이름으로 클릭
  python cdp.py dump                       # 보이는 버튼/옵션 텍스트 덤프
매번 scratch/yt/cdp.png 저장 + 현재 URL 출력."""
import sys, os
from playwright.sync_api import sync_playwright

def main():
    a=sys.argv[1:]
    with sync_playwright() as pw:
        b=pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx=b.contexts[0]
        pg=None
        for p in ctx.pages:
            if "studio.youtube.com" in p.url: pg=p
        if pg is None: pg=ctx.pages[-1] if ctx.pages else ctx.new_page()
        pg.set_default_timeout(8000)
        cmd=a[0] if a else "shot"
        try:
            if cmd=="goto":
                pg.goto(a[1],wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
            elif cmd=="click":
                pg.get_by_text(a[1],exact=False).first.click(); pg.wait_for_timeout(2500)
            elif cmd=="clickxy":
                pg.mouse.click(float(a[1]),float(a[2])); pg.wait_for_timeout(2500)
            elif cmd=="role":
                pg.get_by_role(a[1],name=a[2]).first.click(); pg.wait_for_timeout(2500)
            elif cmd=="rowcell":
                lang,col=a[1],a[2]
                lb=pg.get_by_text(lang,exact=True).first.bounding_box()
                hx=None
                for h in pg.get_by_text(col,exact=True).all():
                    bb=h.bounding_box()
                    if bb and bb["x"]>400: hx=bb["x"]+bb["width"]/2; break
                cy=lb["y"]+lb["height"]/2
                pg.mouse.click(hx,cy); pg.wait_for_timeout(4000); print(f"cell=({round(hx)},{round(cy)})")
            elif cmd=="setfile":
                p=os.path.abspath(a[1]); L=pg.locator("#captions-file-loader"); n=L.count()
                for i in range(n):
                    try: L.nth(i).set_input_files(p); print(f"set[{i}]")
                    except Exception as e: print(f"set[{i}] err {str(e)[:30]}")
                pg.wait_for_timeout(3500)
            elif cmd=="uploadfile":
                # 편집기 '파일 업로드' 옵션 클릭→OS 파일선택기를 가로채 파일 지정
                p=os.path.abspath(a[1])
                with pg.expect_file_chooser(timeout=8000) as fc:
                    pg.get_by_text("파일 업로드",exact=True).first.click()
                fc.value.set_files(p); print("chooser set",os.path.basename(p))
                pg.wait_for_timeout(4000)
            elif cmd=="jsclick":
                # 보이는 요소 중 정확한 텍스트를 가진 버튼/아이템을 JS로 클릭
                t=a[1]
                r=pg.evaluate("""(t)=>{const els=[...document.querySelectorAll('button,tp-yt-paper-item,[role=button],ytcp-button,#continue-button')];for(const e of els){const x=(e.textContent||'').trim();if(x===t){const b=e.getBoundingClientRect();if(b.width>0&&b.height>0){e.click();return 'clicked '+x}}}return 'notfound'}""",t)
                print(r); pg.wait_for_timeout(3500)
            elif cmd=="smartclick":
                # 정확한 텍스트 요소의 CSS 사각형을 구해 그 중심을 실제 마우스로 클릭
                t=a[1]
                rect=pg.evaluate("""(t)=>{const els=[...document.querySelectorAll('button,tp-yt-paper-item,[role=button],ytcp-button,ytcp-button-shape,a,span,div')];let best=null;for(const e of els){const x=(e.textContent||'').trim();if(x===t){const b=e.getBoundingClientRect();if(b.width>0&&b.height>0){if(!best||b.width*b.height<best.w*best.h)best={x:b.x+b.width/2,y:b.y+b.height/2,w:b.width,h:b.height}}}}return best}""",t)
                if rect:
                    pg.mouse.click(rect["x"],rect["y"]); print(f"mouseclick=({round(rect['x'])},{round(rect['y'])})"); pg.wait_for_timeout(3500)
                else: print("notfound")
            elif cmd=="probe":
                t=a[1]
                r=pg.evaluate("""(t)=>{const out=[];document.querySelectorAll('*').forEach(e=>{if((e.textContent||'').trim()===t&&e.children.length<=1){const b=e.getBoundingClientRect();const st=getComputedStyle(e);out.push({tag:e.tagName,id:e.id||'',cls:(e.className||'').toString().slice(0,30),x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),vis:st.visibility,disp:st.display,pe:st.pointerEvents})}});return out.slice(0,12)}""",t)
                import json as _j; print(_j.dumps(r,ensure_ascii=True))
            elif cmd=="atpoint":
                x,y=float(a[1]),float(a[2])
                r=pg.evaluate("""([x,y])=>{const e=document.elementFromPoint(x,y);if(!e)return 'null';return e.tagName+' #'+(e.id||'')+' .'+((e.className||'').toString().slice(0,40))}""",[x,y])
                print("top@",x,y,"=>",r)
            elif cmd=="clickbtn":
                # id로 ytcp-button 클릭 (내부 실제 버튼까지 dispatch)
                bid=a[1]
                r=pg.evaluate("""(bid)=>{const b=document.getElementById(bid);if(!b)return 'noid';const inner=b.querySelector('button, [role=button], .ytcpButtonShapeImpl__button-te')||b;['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t=>inner.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window})));return 'dispatched '+bid}""",bid)
                print(r); pg.wait_for_timeout(3500)
            elif cmd=="key":
                pg.keyboard.press(a[1]); print("pressed",a[1]); pg.wait_for_timeout(3000)
            elif cmd=="dump":
                els=pg.evaluate("""()=>{const o=new Set();document.querySelectorAll('button,tp-yt-paper-item,[role=button],[role=menuitem],a').forEach(e=>{const t=(e.textContent||'').trim();if(t&&t.length<25)o.add(t)});return [...o].slice(0,40)}""")
                print("UI:",els)
            elif cmd=="shot":
                pass
            os.makedirs("scratch/yt",exist_ok=True)
            name=a[-1] if cmd=="shot" and len(a)>1 else "cdp"
            pg.screenshot(path=f"scratch/yt/{name}.png")
            print("URL:",pg.url)
        except Exception as e:
            print("ERR:",str(e)[:120])
            try: pg.screenshot(path="scratch/yt/cdp_err.png")
            except Exception: pass
if __name__=="__main__": main()
