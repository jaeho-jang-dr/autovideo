# -*- coding: utf-8 -*-
"""정형외과TV [대한정형외과학회] 채널 정리 — 제목·내용을 주제/형식별로 분류한다.

목적: 사장님이 앞으로 만들 정형외과 콘텐츠가 **겹치지 않게** 하고,
      비어 있는 주제를 찾는 데 쓴다.

    python research/orthotv_analyze.py            # 표 + 요약
    python research/orthotv_analyze.py --md       # 마크다운 문서 생성
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(ROOT, "ORTHOTV_CATALOG.md")

# ── 부위·주제 분류 사전 ────────────────────────────────────────────────
BODY = {
    "척추": ["척추", "허리", "요추", "경추", "디스크", "협착", "측만", "spine", "lumbar",
             "cervical", "disc", "stenosis", "scoliosis", "목디스크"],
    "무릎": ["무릎", "슬관절", "반월", "십자인대", "knee", "meniscus", "acl", "연골"],
    "어깨": ["어깨", "견관절", "회전근", "오십견", "shoulder", "rotator", "frozen"],
    "고관절": ["고관절", "엉덩이", "대퇴골두", "hip", "femoral head"],
    "손·팔": ["손목", "손가락", "팔꿈치", "터널증후군", "hand", "wrist", "elbow", "carpal"],
    "발·발목": ["발목", "족부", "무지외반", "족저", "ankle", "foot", "plantar", "bunion"],
    "골절·외상": ["골절", "외상", "부러", "fracture", "trauma", "탈구"],
    "골다공증": ["골다공증", "골밀도", "osteoporosis", "bone density"],
    "관절염": ["관절염", "퇴행성", "arthritis", "osteoarthritis", "류마티스"],
    "종양": ["종양", "혹", "육종", "tumor", "sarcoma", "lump"],
    "소아": ["소아", "성장", "아이", "어린이", "pediatric", "growth"],
    "스포츠·운동": ["운동", "스포츠", "재활", "스트레칭", "sport", "exercise",
                   "rehabilitation", "stretch", "workout"],
}
FORMAT = {
    "라이브 Q&A": ["라이브", "live", "ask me anything", "비온뒤"],
    "공모전 수상작": ["awards", "어워드", "공모", "일반영상", "수상"],
    "학회·행사": ["학회", "학술", "expo", "congress", "스케치", "총회", "심포지엄"],
    "교육·강의": ["강의", "лекция", "lecture", "교육", "알아보기", "바로알기"],
    "인터뷰·인물": ["인터뷰", "interview", "교수", "명의"],
    "홍보·안내": ["홍보", "안내", "소개", "캠페인", "공지"],
}


def load(path):
    """원본 dump 가 없으면 슬림본을 읽는다(원본은 59MB 라 깃에 안 올린다)."""
    out = []
    if not os.path.exists(path):
        slim = path.replace(".jsonl", ".slim.jsonl")
        if os.path.exists(slim):
            path = slim
        else:
            return out
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                pass
    return out


def classify(text, table):
    t = text.lower()
    hits = [k for k, ws in table.items() if any(w.lower() in t for w in ws)]
    return hits or ["기타"]


def mmss(sec):
    if not sec:
        return "-"
    m, s = divmod(int(sec), 60)
    return "%d:%02d" % (m, s)


def rows(items, kind):
    out = []
    for v in items:
        title = (v.get("title") or "").strip()
        desc = re.sub(r"\s+", " ", (v.get("description") or "")).strip()
        blob = title + " " + desc[:400]
        out.append({
            "kind": kind,
            "id": v.get("id"),
            "title": title,
            "desc": desc,
            "dur": v.get("duration") or 0,
            "views": v.get("view_count") or 0,
            "date": (v.get("upload_date") or "")[:8],
            "body": classify(blob, BODY),
            "fmt": classify(blob, FORMAT),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    vids = rows(load(os.path.join(ROOT, "orthotv_videos.jsonl")), "영상")
    shorts = rows(load(os.path.join(ROOT, "orthotv_shorts.jsonl")), "쇼츠")
    allv = sorted(vids + shorts, key=lambda r: r["date"], reverse=True)

    body_c, fmt_c = Counter(), Counter()
    for r in allv:
        for b in r["body"]:
            body_c[b] += 1
        for f in r["fmt"]:
            fmt_c[f] += 1

    print("정형외과TV [대한정형외과학회] — 영상 %d · 쇼츠 %d · 합계 %d"
          % (len(vids), len(shorts), len(allv)))
    print("기간 %s ~ %s" % (min(r["date"] for r in allv if r["date"]),
                            max(r["date"] for r in allv if r["date"])))
    print("\n[부위·주제]")
    for k, n in body_c.most_common():
        print("  %-10s %3d편" % (k, n))
    print("\n[형식]")
    for k, n in fmt_c.most_common():
        print("  %-12s %3d편" % (k, n))
    print("\n[조회수 상위 15]")
    for r in sorted(allv, key=lambda x: -x["views"])[:15]:
        print("  %8d회 %-4s %-6s %s" % (r["views"], r["kind"], mmss(r["dur"]),
                                        r["title"][:58]))

    if a.md:
        write_md(vids, shorts, allv, body_c, fmt_c)
        print("\n→", OUT_MD)
    return 0


def write_md(vids, shorts, allv, body_c, fmt_c):
    L = []
    L.append("# 정형외과TV [대한정형외과학회] — 콘텐츠 카탈로그\n")
    L.append("> 채널 `UC8kfC5zv1Mo_3DcBbhEIfqw` · 구독자 5,660 · "
             "영상 %d + 쇼츠 %d = **%d편**\n" % (len(vids), len(shorts), len(allv)))
    L.append("> 목적 — 앞으로 만들 정형외과 콘텐츠가 **겹치지 않게** 하고 빈 주제를 찾는다.\n")

    L.append("\n## 1. 한눈에\n")
    L.append("| 부위·주제 | 편수 | | 형식 | 편수 |")
    L.append("|---|---:|---|---|---:|")
    b = body_c.most_common()
    f = fmt_c.most_common()
    for i in range(max(len(b), len(f))):
        bk, bn = b[i] if i < len(b) else ("", "")
        fk, fn = f[i] if i < len(f) else ("", "")
        L.append("| %s | %s | | %s | %s |" % (bk, bn, fk, fn))

    L.append("\n## 2. 조회수 상위 20\n")
    L.append("| 조회 | 구분 | 길이 | 제목 |")
    L.append("|---:|---|---|---|")
    for r in sorted(allv, key=lambda x: -x["views"])[:20]:
        L.append("| %s | %s | %s | [%s](https://youtu.be/%s) |"
                 % (f"{r['views']:,}", r["kind"], mmss(r["dur"]),
                    r["title"].replace("|", "/")[:70], r["id"]))

    L.append("\n## 3. 부위·주제별 전체 목록\n")
    by = defaultdict(list)
    for r in allv:
        by[r["body"][0]].append(r)
    for k in [x for x, _ in body_c.most_common()]:
        if k not in by:
            continue
        L.append("\n### %s (%d편)\n" % (k, len(by[k])))
        L.append("| 날짜 | 구분 | 길이 | 조회 | 제목 |")
        L.append("|---|---|---|---:|---|")
        for r in sorted(by[k], key=lambda x: x["date"], reverse=True):
            L.append("| %s | %s | %s | %s | [%s](https://youtu.be/%s) |"
                     % (r["date"], r["kind"], mmss(r["dur"]), f"{r['views']:,}",
                        r["title"].replace("|", "/")[:70], r["id"]))

    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
