#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
글씨랑 (Geulssirang) — 한글교육 글자 통합 에이전트.

세 덩어리를 하나의 API로 통합한다:
  1) 전용 폰트 6종 (assets/fonts, DB hangeul_fonts)
  2) 파라메트릭 드로잉 엔진 (font_write=폰트글자꼴 / hangeul_write=획순 / hangeul_strokes=모음)
  3) 글자 데이터베이스 (hangeul_stroke_order, hangeul_stroke_principle, hangeul_jamo, hangeul_audio_assets)

★ 렌더링 정책(사장님 확정, 절대준수):
  - 자막·텍스트박스 = 구글/시스템 기본 폰트(malgun) 그대로.  (SUBTITLE_FONT/TEXTBOX_FONT)
  - 파라메트릭 드로잉만 = 우리 6종 폰트로 다양하게.
  - 비틀린/이상한 글자 절대 금지 → 폰트 글자꼴(font_write)로 정확·예쁘게. 이건 한글교육이다.

API:
  gs = Geulssirang()
  gs.fonts()                          # 등록 폰트 목록
  gs.draw(text, style='nanum_pen', size=120, progress=0.6)   # 파라메트릭 드로잉(RGBA)
  gs.draw(text, style='stroke', ...)  # 획순 교육 드로잉(자모/음절)
  gs.stroke_order('강')               # DB 획순 데이터
  gs.principles()                     # 획순 원칙
  gs.role_font('title'|'draw'|'brush'|'body')   # 용도별 권장 폰트키
"""
import os, sqlite3
ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")

# ── 렌더링 정책(구글/시스템 기본) ──
SUBTITLE_FONT = "C:/Windows/Fonts/malgun.ttf"   # 자막: 손대지 않음
TEXTBOX_FONT  = "C:/Windows/Fonts/malgun.ttf"   # 텍스트박스(캡션/노트): 기본

# 용도별 권장 폰트키 (파라메트릭 드로잉 전용)
ROLE_FONT = {
    "title": "black_han_sans",     # 타이틀/제목
    "draw":  "nanum_pen",          # 핵심 글자 드로잉(친근+또렷)
    "round": "cafe24_dongdong",    # 둥근 손글씨
    "brush": "nanum_brush",        # 붓글씨(쓰기연습)
    "body":  "nanum_gothic",       # 본문 보조
    "round_gothic": "cafe24_ssurround",
}


class Geulssirang:
    def __init__(self, db=DB):
        self.db = db
        import font_write, hangeul_write
        self._fw = font_write
        self._hw = hangeul_write

    # ── 폰트 ──
    def fonts(self):
        con = sqlite3.connect(self.db); con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(
            "SELECT key,korean_name,family,file_path,category,license,use_for FROM hangeul_fonts ORDER BY id")]
        con.close(); return rows

    def role_font(self, role):
        return ROLE_FONT.get(role, "nanum_pen")

    # ── 파라메트릭 드로잉 ──
    def draw(self, text, style="nanum_pen", size=120, progress=1.0, pen=True):
        """style: 폰트키(폰트글자꼴 드로잉, 안 비틀림) 또는 'stroke'(획순 교육 드로잉)."""
        if style == "stroke":
            return self._hw.render_syllable(text, size, progress=progress)
        return self._fw.render_text_writing(text, style, size, progress=progress, pen=pen)

    def can_stroke(self, text):
        """획순 stroke 드로잉 가능한지(자모/음절 획 정의 보유)."""
        return self._hw.can_write(text)

    # ── 글자 DB ──
    def stroke_order(self, char):
        con = sqlite3.connect(self.db); con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(
            "SELECT stroke_no,n_strokes,points_json,direction FROM hangeul_stroke_order "
            "WHERE char=? ORDER BY stroke_no", (char,))]
        con.close(); return rows

    def principles(self):
        con = sqlite3.connect(self.db)
        rows = [r[0] for r in con.execute("SELECT rule FROM hangeul_stroke_principle ORDER BY id")]
        con.close(); return rows

    def jamo(self, ja):
        con = sqlite3.connect(self.db); con.row_factory = sqlite3.Row
        r = con.execute("SELECT * FROM hangeul_jamo WHERE jamo=?", (ja,)).fetchone()
        con.close(); return dict(r) if r else None


def _manifest():
    """geulssirang 구성요소를 DB에 등록(통합 매니페스트)."""
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS geulssirang_manifest(
        id INTEGER PRIMARY KEY, component TEXT, kind TEXT, ref TEXT, note TEXT, updated_at TEXT)""")
    cur.execute("DELETE FROM geulssirang_manifest")
    m = [
        ("fonts", "table", "hangeul_fonts", "전용 폰트 6종(검은고딕/나눔고딕/나눔펜/나눔붓/카페24동동/써라운드)"),
        ("draw_font", "module", "font_write.py", "폰트 글자꼴 파라메트릭 드로잉(안 비틀림)"),
        ("draw_stroke", "module", "hangeul_write.py", "자음+음절 정획순 드로잉(획순 교육)"),
        ("draw_vowel", "module", "hangeul_strokes.py", "모음 정획순 드로잉"),
        ("stroke_db", "table", "hangeul_stroke_order", "33자 96획 상세"),
        ("principle_db", "table", "hangeul_stroke_principle", "획순 5원칙"),
        ("jamo_db", "table", "hangeul_jamo", "자모 이름·소리(남/여)"),
        ("audio_db", "table", "hangeul_audio_assets", "발음 클립(선희)"),
        ("api", "module", "geulssirang.py", "통합 진입점 Geulssirang()"),
        ("policy", "rule", "subtitle/textbox=google-default, param-draw=our-fonts, no-distorted-glyph", "한글교육: 비틀린 글자 금지"),
    ]
    for c, k, r, n in m:
        cur.execute("INSERT INTO geulssirang_manifest(component,kind,ref,note,updated_at) VALUES (?,?,?,?,datetime('now'))",
                    (c, k, r, n))
    con.commit()
    print("geulssirang_manifest:", cur.execute("SELECT count(*) FROM geulssirang_manifest").fetchone()[0], "components")
    con.close()


if __name__ == "__main__":
    _manifest()
    gs = Geulssirang()
    print("\n[글씨랑 Geulssirang] 통합 확인")
    print("폰트:", ", ".join(f"{f['korean_name']}({f['key']})" for f in gs.fonts()))
    print("용도별:", {r: gs.role_font(r) for r in ("title", "draw", "brush", "body")})
    print("원칙:")
    for p in gs.principles():
        print("  -", p)
    print("'강' 획순:", len(gs.stroke_order("강")), "행(음절), 자모별 stroke DB 보유")
