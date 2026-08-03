# -*- coding: utf-8 -*-
"""W24 — Flow 캐릭터 등록 자동화 (2026-07-28).

Flow 좌측 `캐릭터 → 신규 캐릭터 → 업로드` 로 정면 1장을 올려 캐릭터를 등록한다.
등록해 두면 프롬프트에서 `@이름` 으로 불러 일관성 있게 재사용할 수 있다.
★참조 제한: Omni Flash 최대 7개 / Veo 3.1 최대 3개 → 7캐릭터 동시 등장은 Omni Flash 필수.

사용:
  python flow_register_chars.py list            # 등록 대상 확인
  python flow_register_chars.py one stickman    # 하나만 등록(검증용)
  python flow_register_chars.py all             # 전부 등록
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
GUIDE_DIR = "W24/characters"
SH = "scratch/yt"
os.makedirs(SH, exist_ok=True)

# (호출명, 파일, 설명 텍스트)
CHARS = [
    ("stickman", "stickman.png",
     "A simple hand-drawn stick figure: a thin outlined round head with two dot eyes and a small "
     "smile, thin black ink limbs, no clothes, white background"),
    ("zollaman", "zollaman.png",
     "A hand-drawn stick figure with a solid black round head of hair, thin black ink limbs and "
     "small round hands and feet, no clothes, white background"),
    ("zollagirl", "zollagirl.png",
     "A hand-drawn stick figure with an outlined round head and an orange hair bun, thin black ink "
     "limbs and small round hands and feet, no clothes, white background"),
    ("injun", "injun.png",
     "A cartoon young Korean man in a navy short-sleeve t-shirt, beige trousers and white sneakers, "
     "short black hair, flat colours with clean black outlines"),
    ("jieun", "jieun.png",
     "A cartoon young Korean woman in a yellow floral dress, long wavy brown hair, flat colours "
     "with clean black outlines"),
    ("madamjay", "madamjay.png",
     "A cartoon Korean woman teacher, brown hair in a bun, coral apron over a white skirt, "
     "flat colours with clean black outlines"),
    ("teacherjay", "teacherjay.png",
     "A cartoon Korean man teacher with a bald head and one curl of hair, blue checked shirt, "
     "beige trousers and grey sneakers, flat colours with clean black outlines"),
]


def log(m):
    print(m, flush=True)


def shot(pg, n):
    try:
        pg.screenshot(path=f"{SH}/reg_{n}.png", timeout=20000, animations="disabled")
    except Exception:
        pass


def click_text(pg, txt, exact=True):
    return pg.evaluate("""([txt, exact]) => {
        const els = [...document.querySelectorAll('*')].filter(e =>
            e.children.length === 0 &&
            (exact ? (e.innerText||'').trim() === txt : (e.innerText||'').includes(txt)));
        if (!els.length) return false;
        (els[0].closest('button,[role=button],div') || els[0]).click();
        return true;
    }""", [txt, exact])


def register(pg, name, fname, desc):
    path = os.path.abspath(os.path.join(GUIDE_DIR, fname))
    if not os.path.exists(path):
        log(f"  ★파일 없음: {path}"); return False

    log(f"--- {name} 등록 시작")
    # 1) ★매번 프로젝트 루트로 돌아간 뒤 캐릭터 목록 → 신규 캐릭터.
    #    이전 캐릭터 편집기(/character/<id>)에 머물면 '신규 캐릭터'가 없어 업로드 버튼을 못 찾는다.
    root = pg.url.split("/character")[0]
    pg.goto(root, wait_until="domcontentloaded")
    time.sleep(10)
    ok = pg.evaluate("""() => {
        const el = [...document.querySelectorAll('span')]
            .find(e => (e.innerText||'').trim() === '캐릭터' && e.getBoundingClientRect().x < 340);
        if (!el) return false;
        (el.closest('button,[role=button],a,div') || el).click();
        return true;
    }""")
    if not ok:
        log("  ★'캐릭터' 메뉴 못 찾음"); return False
    time.sleep(5)
    click_text(pg, "신규 캐릭터")
    time.sleep(4)
    shot(pg, f"{name}_1_panel")

    # 2) 업로드 — 파일 선택창을 가로채 경로를 직접 넣는다
    try:
        with pg.expect_file_chooser(timeout=15000) as fc:
            if not click_text(pg, "업로드"):
                log("  ★'업로드' 버튼 못 찾음"); return False
        fc.value.set_files(path)
        log(f"  업로드: {fname}")
    except Exception as e:
        log(f"  ★파일 선택 실패 {str(e)[:60]}"); return False
    time.sleep(8)
    shot(pg, f"{name}_2_uploaded")

    # 3) 설명 — ★편집기가 늦게 뜬다. textarea 가 나타날 때까지 재시도한다(한 번만 하면 늘 실패)
    ok = False
    for _ in range(8):
        ok = pg.evaluate("""(d) => {
            const t = [...document.querySelectorAll('textarea')]
                .find(x => (x.placeholder||'').includes('캐릭터의 행동'));
            if (!t) return false;
            const set = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
            set.call(t, d);
            t.dispatchEvent(new Event('input', {bubbles:true}));
            t.dispatchEvent(new Event('change', {bubbles:true}));
            return true;
        }""", desc)
        if ok:
            break
        time.sleep(3)
    log(f"  설명 입력: {ok}")
    time.sleep(2)

    # 4) 이름 — 제목 옆 연필(edit) → 입력 → Enter
    pg.evaluate("""() => { const e = [...document.querySelectorAll('button')]
        .find(x => (x.innerText||'').trim() === 'edit'); if (e) e.click(); }""")
    time.sleep(2)
    named = pg.evaluate("""(n) => {
        const i = [...document.querySelectorAll('input')]
            .find(x => x.getBoundingClientRect().width > 60);
        if (!i) return false;
        const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        set.call(i, n);
        i.dispatchEvent(new Event('input', {bubbles:true}));
        i.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
    }""", name)
    pg.keyboard.press("Enter")
    time.sleep(3)
    shot(pg, f"{name}_4_named")

    got = pg.evaluate("""() => [...document.querySelectorAll('span')]
        .map(e => (e.innerText||'').trim()).filter(Boolean)""")
    ok2 = name in got
    log(f"  이름 '{name}' 반영: {ok2}")

    # 5) 완료 → 캐릭터 목록으로 복귀(다음 캐릭터 등록 준비)
    click_text(pg, "완료")
    time.sleep(5)
    return ok2


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode == "list":
        for n, f, _ in CHARS:
            p = os.path.join(GUIDE_DIR, f)
            print(f"  @{n:12s} {'有' if os.path.exists(p) else '★없음'}  {p}")
        return
    targets = CHARS if mode == "all" else [c for c in CHARS if c[0] == sys.argv[2]]
    if not targets:
        raise SystemExit("대상 없음")
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        # ★탭이 여러 개면 엉뚱한 탭을 잡는다 → 프로젝트 탭을 앞으로 가져오고,
        #   좌측 레일('캐릭터')이 실제로 보일 때까지 확인한다.
        # ★탭이 10개씩 열려 있다 — '/character' 화면이 이미 열린 탭을 최우선으로 잡는다
        pg = (next((p for p in ctx.pages if "/character" in p.url), None)
              or next((p for p in ctx.pages if "/project/" in p.url), None))
        if pg is None:
            pg = ctx.new_page()
            pg.goto("https://labs.google/fx/ko/tools/flow", wait_until="domcontentloaded")
            time.sleep(12)
        pg.bring_to_front()
        time.sleep(2)
        log(f"URL: {pg.url[:80]}")
        for n, f, d in targets:
            register(pg, n, f, d)
            time.sleep(3)


if __name__ == "__main__":
    main()
