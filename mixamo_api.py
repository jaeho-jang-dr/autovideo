# -*- coding: utf-8 -*-
"""mixamo_api.py — Mixamo 내부 API로 동작 FBX 다운로드(무료, 웹과 동일). 토큰=scratch/mx_auth.json.
사용:
  python mixamo_api.py search "walk"                 # 검색
  python mixamo_api.py get "Walking" walk_mx [inplace]  # 정확한 이름으로 받기
  python mixamo_api.py batch                          # 요청 동작 일괄
"""
import sys, os, json, time
import requests
import sys as _s
try:_s.stdout.reconfigure(encoding="utf-8")
except:pass

AUTH = json.load(open("scratch/mx_auth.json"))
H = {"Authorization": AUTH["token"], "X-Api-Key": AUTH["apikey"] or "mixamo2",
     "Accept": "application/json", "Content-Type": "application/json",
     "X-Requested-With": "XMLHttpRequest",
     "User-Agent": "Mozilla/5.0"}
CHAR = AUTH["charid"]
DL = os.path.abspath("scratch/mocap"); os.makedirs(DL, exist_ok=True)
API = "https://www.mixamo.com/api/v1"
def log(m): print(m, flush=True)


def search(q, limit=16):
    r = requests.get(f"{API}/products", headers=H,
        params={"page": 1, "limit": limit, "order": "", "type": "Motion,MotionPack", "query": q})
    r.raise_for_status()
    return r.json().get("results", [])


def get_details(anim_id):
    r = requests.get(f"{API}/products/{anim_id}", headers=H,
        params={"similar": 0, "character_id": CHAR})
    r.raise_for_status()
    return r.json()["details"]


def export_download(anim_id, name, out_name, fps=30, inplace=True, skin=False):
    det = get_details(anim_id)
    g = det["gms_hash"]
    # params: [["Overdrive",0.0],...] → 값만 콤마문자열 "0", overdrive 필드 분리
    plist = g.get("params", [])
    params_str = ",".join(str(v) for _, v in plist)
    overdrive = 0
    for nm2, v in plist:
        if str(nm2).lower() == "overdrive":
            overdrive = v
    gms = {
        "model-id": g["model-id"],
        "mirror": g.get("mirror", False),
        "trim": g.get("trim", [0, 100]),
        "overdrive": overdrive,
        "params": params_str,
        "arm-space": g.get("arm-space", 0),
        "inplace": inplace,
    }
    payload = {
        "character_id": CHAR,
        "gms_hash": [gms],
        "preferences": {"format": "fbx7", "skin": ("true" if skin else "false"), "fps": str(fps), "reducekf": "0"},
        "product_name": name,
        "type": "Motion",
    }
    r = requests.post(f"{API}/animations/export", headers=H, data=json.dumps(payload))
    if r.status_code not in (200, 202):
        log(f"  export 실패 {r.status_code}: {r.text[:120]}"); return False
    # monitor
    for i in range(90):
        m = requests.get(f"{API}/characters/{CHAR}/monitor", headers=H)
        try: j = m.json()
        except Exception: j = {}
        st = j.get("status")
        if st == "completed":
            url = j["job_result"]
            data = requests.get(url).content
            out = os.path.join(DL, f"{out_name}.fbx")
            open(out, "wb").write(data)
            log(f"  ✔ {out_name}.fbx ({len(data)//1024}KB)"); return True
        if st == "failed":
            log(f"  export failed: {j}"); return False
        time.sleep(2)
    log("  monitor 타임아웃"); return False


def find_exact(q, want):
    """검색결과에서 want(정확/근접)한 Motion 하나 반환 (id, name)."""
    res = search(q)
    # 정확 일치 우선
    for r in res:
        if r.get("type") == "Motion" and r["name"].strip().lower() == want.strip().lower():
            return r["id"], r["name"]
    for r in res:
        if r.get("type") == "Motion":
            return r["id"], r["name"]
    return (res[0]["id"], res[0]["name"]) if res else (None, None)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "search"
    if mode == "search":
        for r in search(sys.argv[2]):
            log(f"  [{r.get('type')}] {r['name']}  id={r['id']}")
    elif mode == "get":
        want = sys.argv[2]; out = sys.argv[3] if len(sys.argv) > 3 else "anim"
        inplace = (sys.argv[4].lower() == "inplace") if len(sys.argv) > 4 else True
        skin = ("skin" in sys.argv[4:]) if len(sys.argv) > 4 else False
        aid, nm = find_exact(want, want)
        if not aid: log("검색 결과 없음"); sys.exit(1)
        log(f"→ {nm} (id={aid}) inplace={inplace} skin={skin}")
        export_download(aid, nm, out, inplace=inplace, skin=skin)
