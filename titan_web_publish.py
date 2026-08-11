# -*- coding: utf-8 -*-
"""titan_science → 웹사이트 반영. CA-002 행에 유튜브 ID·제목·상태를 넣고 export.

    python titan_web_publish.py
"""
import os
import sqlite3
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PKG = "titan_science/pkg"
DB = "channel/content.db"


def read(p):
    return open(p, encoding="utf-8").read().strip()


def main():
    ko = read(f"{PKG}/vid_ko.txt")
    en = read(f"{PKG}/vid_en.txt")
    c = sqlite3.connect(DB)
    c.execute("""UPDATE episodes SET
                   title_kr=?, title_en=?, hook_kr=?, status='published',
                   runtime_sec=?, youtube_kr=?, youtube_en=?
                 WHERE code='CA-002'""",
              (read(f"{PKG}/ko_title.txt"),
               read(f"{PKG}/en_title.txt"),
               "60미터 거인의 팔은 왜 종이 상자처럼 튀어 오를까? "
               "제곱-세제곱 법칙이 거인에게 내린 판결을 8분에 담았습니다.",
               486, ko, en))
    c.commit()
    r = c.execute("""SELECT code,status,youtube_kr,youtube_en,runtime_sec
                     FROM episodes WHERE code='CA-002'""").fetchone()
    print("DB 갱신:", r)
    c.close()

    subprocess.run(["python", "channel/export_web.py"], check=True)
    print("web/src/data/content.json 갱신 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
