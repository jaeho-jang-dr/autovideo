# -*- coding: utf-8 -*-
"""mixamo_token.py — 로그인된 프로필에서 Mixamo API 토큰 + character_id 추출 → scratch/mx_auth.json 저장."""
import sys, os, json, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SH = "scratch/mx"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
cap = {"token": None, "apikey": None, "charid": None}

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="en-US", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()

    def on_req(req):
        u = req.url
        if "mixamo.com/api" in u:
            h = req.headers
            if h.get("authorization"): cap["token"] = h["authorization"]
            if h.get("x-api-key"): cap["apikey"] = h["x-api-key"]
            # /characters/{id}/ 형태에서 char id
            import re
            m = re.search(r"/characters/([0-9a-fA-F-]{20,})", u)
            if m and not cap["charid"]: cap["charid"] = m.group(1)
    pg.on("request", on_req)

    pg.set_default_timeout(40000)
    pg.goto("https://www.mixamo.com/#/", wait_until="domcontentloaded")
    pg.wait_for_timeout(12000)                          # 초기 API 호출들 발생 대기
    # 캐릭터 로드 유도(검색 한번)
    try:
        pg.locator("input[placeholder*='Search']").first.fill("walking"); pg.keyboard.press("Enter")
        pg.wait_for_timeout(8000)
    except Exception: pass
    log("token: " + (cap["token"][:40]+"..." if cap["token"] else "None"))
    log("apikey: " + str(cap["apikey"]))
    log("charid: " + str(cap["charid"]))
    if cap["token"]:
        json.dump(cap, open("scratch/mx_auth.json", "w"))
        log("→ scratch/mx_auth.json 저장")
    ctx.close()
