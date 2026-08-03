# -*- coding: utf-8 -*-
"""★W24 Flow 캐릭터 7종 등록 — 파일 다이얼로그 우회판 (2026-08-03).

`flow_register_chars.py` 의 **절차를 그대로** 쓰고 딱 한 군데만 고쳤다(주차별 복제 관례):
  ★`expect_file_chooser` 가 15초 타임아웃으로 7전 7패 → 숨은 `input[type=file]` 에
    **직접 set_input_files** 한다(= flow_driver.upload 가 쓰는, 검증된 방식).
  ★`click_text` 의 `closest('button,[role=button],div')` 는 버튼 대신 DIV 를 물어
    클릭이 먹지 않았다 → DIV 를 뺀다.

★설명문은 `W24/clip5_prompt.txt` 의 7인 묘사와 **문구를 맞췄다.** 등록 설명과 프롬프트
  묘사가 어긋나면 캐릭터가 흔들린다(사장님 지시: 일관성 유지가 최우선).

사용:
  python flow_register_chars_w24.py list
  python flow_register_chars_w24.py one stickman
  python flow_register_chars_w24.py all
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

# (호출명, 파일, 설명) — ★설명은 clip5_prompt.txt 의 7인 묘사와 동일 문구
CHARS = [
    ("teacherjay", "teacherjay.png",
     "A coloured cartoon man, bald head with a single curl of hair, blue and white checked shirt "
     "with rolled sleeves, beige trousers, white sneakers. Flat 2D cartoon illustration with bold "
     "clean black outlines and flat colours."),
    ("zollaman", "zollaman.png",
     "A hand-drawn black ink stick figure with thin ink limbs and no clothes, his head filled solid "
     "black like a bowl cut. A simple line drawing, never a coloured person."),
    ("zollagirl", "zollagirl.png",
     "A hand-drawn black ink stick figure with thin ink limbs and no clothes, her head an open white "
     "circle with bright orange hair tied in a bun. A simple line drawing, never a coloured person."),
    ("stickman", "stickman.png",
     "The plainest BLACK LINE STICK FIGURE drawn in thick smooth ink strokes: an empty white circle for a head with two dot eyes and a small smile, a straight line body, thin straight line arms and legs, no hair, no hands, no feet, no clothes. He is a PERSON, never an object and never a pen. His ink lines glow softly cyan."),
    ("injun", "injun.png",
     "A coloured cartoon young man, tall and slim, short black hair, navy blue t-shirt, beige "
     "trousers, white sneakers. Flat 2D cartoon illustration with bold clean black outlines."),
    ("jieun", "jieun.png",
     "A coloured cartoon young woman, long wavy light brown hair, pale yellow floral dress. "
     "Flat 2D cartoon illustration with bold clean black outlines and flat colours."),
    ("madamjay", "madamjay.png",
     "A coloured cartoon woman who looks about forty, smooth youthful face, rosy cheeks, big warm "
     "smile, glossy dark brown hair in a neat bun, vivid coral sleeveless vest over a white blouse, "
     "white knee-length skirt. Flat 2D cartoon illustration with bold clean black outlines."),
]


def log(m):
    print(m, flush=True)


def shot(pg, n):
    try:
        pg.screenshot(path=f"{SH}/w24reg_{n}.png", timeout=20000, animations="disabled")
    except Exception:
        pass


def click_text(pg, txt, exact=True):
    """★DIV 를 빼고 진짜 버튼만 클릭한다."""
    return pg.evaluate("""([txt, exact]) => {
        const els = [...document.querySelectorAll('*')].filter(e =>
            e.children.length === 0 &&
            (exact ? (e.innerText||'').trim() === txt : (e.innerText||'').includes(txt)));
        for (const el of els) {
            const b = el.closest('button,[role=button],a');
            if (b) { b.click(); return true; }
        }
        return false;
    }""", [txt, exact])


def open_new_character(pg):
    """프로젝트 루트 → 좌측 레일 '캐릭터' → '신규 캐릭터'."""
    root = pg.url.split("/character")[0]
    pg.goto(root, wait_until="domcontentloaded")
    time.sleep(9)
    ok = pg.evaluate("""() => {
        const el = [...document.querySelectorAll('span')]
            .find(e => (e.innerText||'').trim() === '캐릭터' && e.getBoundingClientRect().x < 340);
        if (!el) return false;
        (el.closest('button,[role=button],a,div') || el).click();
        return true;
    }""")
    if not ok:
        return False
    time.sleep(6)
    # ★'신규 캐릭터'는 버튼이 아니라 **카드**다 → click_text(closest button) 로는 안 눌린다.
    #   Playwright 로케이터로 진짜 마우스 클릭을 보낸다.
    try:
        pg.get_by_text("신규 캐릭터", exact=True).first.click(timeout=10000)
    except Exception as e:
        log(f"  ★'신규 캐릭터' 클릭 실패 {str(e)[:60]}"); return False
    time.sleep(5)
    return True


def register(pg, name, fname, desc):
    path = os.path.abspath(os.path.join(GUIDE_DIR, fname))
    if not os.path.exists(path):
        log(f"  ★파일 없음: {path}"); return False

    log(f"--- {name} 등록 시작")
    if not open_new_character(pg):
        log("  ★'캐릭터' 메뉴 못 찾음"); return False
    shot(pg, f"{name}_1_panel")

    # ★업로드 — '업로드' **버튼**을 Playwright 로케이터로 눌러 파일 다이얼로그를 가로챈다.
    #   원본이 쓰던 click_text 는 closest('…,div') 때문에 DIV 를 눌러 7전 7패였다.
    #   페이지의 input[type=file] 에 직접 주입하는 방식도 안 된다(그 input 은 캐릭터용이 아니다).
    try:
        with pg.expect_file_chooser(timeout=20000) as fc:
            pg.locator("button:has-text('업로드')").first.click()
        fc.value.set_files(path)
        log(f"  업로드: {fname}")
    except Exception as e:
        log(f"  ★업로드 실패 {str(e)[:70]}"); return False

    # ★권리 확인 다이얼로그('알림 … 필요한 권리가 있는지 확인하세요') — 뜨면 '동의함'.
    #   ★보이는 것만 누른다. DOM 에는 크기 0 짜리 죽은 '동의함' 버튼이 상시 남아 있다.
    for _ in range(6):
        clicked = pg.evaluate("""() => {
            for (const b of document.querySelectorAll('button,[role=button],a')) {
                if ((b.innerText||'').trim() === '동의함' && b.getBoundingClientRect().width > 0) {
                    b.click(); return true;
                }
            }
            return false;
        }""")
        if clicked:
            log("  권리 확인 동의"); time.sleep(2); break
        time.sleep(2)
    shot(pg, f"{name}_2_uploaded")

    # 설명 — ★편집기가 늦게 뜬다. textarea 가 나타날 때까지 재시도
    okd = False
    for _ in range(20):
        okd = pg.evaluate("""(d) => {
            const t = [...document.querySelectorAll('textarea')]
                .find(x => (x.placeholder||'').includes('캐릭터의 행동'));
            if (!t) return false;
            const set = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
            set.call(t, d);
            t.dispatchEvent(new Event('input', {bubbles:true}));
            t.dispatchEvent(new Event('change', {bubbles:true}));
            return true;
        }""", desc)
        if okd:
            break
        time.sleep(3)
    log(f"  설명 입력: {okd}")
    time.sleep(2)

    # 이름 — 제목 옆 연필(edit) → ★키보드로 직접 타이핑 → Enter
    #   (프로그램적 value 주입은 화면엔 보여도 저장이 안 된다 — 'Untitled Character' 로 남는다)
    try:
        pg.locator("button:has-text('edit')").first.click(timeout=8000)
        time.sleep(2)
        inp = pg.locator("input:visible").first
        inp.click(); time.sleep(0.3)
        inp.press("Control+a"); inp.press("Delete")
        pg.keyboard.type(name, delay=60)
        time.sleep(0.5)
        pg.keyboard.press("Enter")
        time.sleep(2)
    except Exception as e:
        log(f"  ★이름 입력 실패 {str(e)[:60]}")
    shot(pg, f"{name}_3_named")

    # ★'완료'가 저장이다. 안 누르면 이름도 설명도 날아간다.
    try:
        pg.locator("button:has-text('완료')").first.click(timeout=8000)
        time.sleep(6)
    except Exception as e:
        log(f"  ★'완료' 클릭 실패 {str(e)[:60]}"); return False
    log(f"  저장(완료) — {name}")
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode == "list":
        for n, f, _ in CHARS:
            p = os.path.join(GUIDE_DIR, f)
            print(f"  @{n:12s} {'有' if os.path.exists(p) else '★없음'}  {p}")
        return
    want = set(sys.argv[2:])
    targets = CHARS if mode == "all" else [c for c in CHARS if c[0] in want]
    if not targets:
        raise SystemExit("대상 없음")
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        pg = (next((p for p in ctx.pages if "/character" in p.url), None)
              or next((p for p in ctx.pages if "/project/" in p.url), None))
        if pg is None:
            raise SystemExit("프로젝트 탭이 없다 — Flow 프로젝트를 먼저 연다")
        pg.bring_to_front()
        time.sleep(2)
        log(f"URL: {pg.url[:80]}")
        done = []
        for n, f, d in targets:
            if register(pg, n, f, d):
                done.append(n)
            time.sleep(3)
        log(f"\n등록 완료 {len(done)}/{len(targets)}: {', '.join(done)}")


if __name__ == "__main__":
    main()
