# -*- coding: utf-8 -*-
"""전용 OAuth 클라이언트로 유튜브 토큰 발급 → yt_token.json 저장(재사용).
브라우저가 열리면 drjang00으로 로그인 → '확인되지 않은 앱' 뜨면 고급→이동→허용."""
import sys, glob, os, json
from google_auth_oauthlib.flow import InstalledAppFlow
ROOT = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
cs = sorted(glob.glob(os.path.join(ROOT, "client_secret_*.json")))
if not cs:
    print("client_secret json 없음"); sys.exit(1)
CS = cs[0]
ctype = list(json.load(open(CS, encoding="utf-8")).keys())[0]
print("client secret:", os.path.basename(CS), "/ type:", ctype)
flow = InstalledAppFlow.from_client_secrets_file(CS, SCOPES)
creds = flow.run_local_server(
    port=0, open_browser=True, prompt="consent",
    authorization_prompt_message="\n>>> 브라우저에서 승인하세요. 안 열리면 이 URL 방문:\n{url}\n",
    success_message="인증 완료 — 이 창은 닫아도 됩니다.")
open(os.path.join(ROOT, "yt_token.json"), "w", encoding="utf-8").write(creds.to_json())
print("TOKEN SAVED: yt_token.json")
