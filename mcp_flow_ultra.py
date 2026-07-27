# -*- coding: utf-8 -*-
"""mcp_flow_ultra — Ultra 계정 Flow(Veo) 동영상 생성을 MCP 툴로 노출(autoveo_flow.py 래핑).
API 과금 없이 Ultra 구독 크레딧으로 생성. 대화창/에이전트에서 generate_flow_video(...) 호출.
등록: .claude/settings.json 의 mcpServers 에 flow-ultra 로 추가(python mcp_flow_ultra.py).
"""
import os, subprocess, sys
from mcp.server.fastmcp import FastMCP

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
mcp = FastMCP("flow-ultra")


def _run(args, timeout=900):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "autoveo_flow.py")] + args,
                       cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    tail = (p.stdout or "")[-1500:] + (("\n[ERR]\n" + (p.stderr or "")[-800:]) if p.returncode else "")
    return f"rc={p.returncode}\n{tail}"


@mcp.tool()
def generate_flow_video(prompts_file: str = "prompts_for_veo.txt", aspect: str = "16:9",
                        profile_cycle: str = "0,1,0,2,0,3,0,4", scene: int = 0) -> str:
    """Flow(Veo)로 프롬프트 파일 기반 동영상 생성(Ultra 크레딧, API 과금 없음).
    prompts_file: '[Scene N] <이미지프롬프트> :: <모션프롬프트>' 형식. aspect 16:9/9:16.
    profile_cycle: 6계정 라운드로빈(차단회피). scene>0 이면 그 씬만 생성."""
    args = ["--prompts", prompts_file, "--aspect", aspect]
    if profile_cycle:
        args += ["--profile-cycle", profile_cycle]
    if scene:
        args += ["--scene", str(scene), "--force"]
    return _run(args)


@mcp.tool()
def animate_image(image_path: str, motion: str, aspect: str = "9:16",
                  prompts_file: str = "prompts_for_veo.txt", scene: int = 1,
                  profile_idx: int = 0) -> str:
    """업로드한 이미지를 첫 프레임으로 애니메이션(캐릭터/배경 동작 동영상). motion=모션 프롬프트."""
    args = ["--prompts", prompts_file, "--scene", str(scene), "--force",
            "--upload", image_path, "--motion", motion, "--aspect", aspect,
            "--profile-idx", str(profile_idx)]
    return _run(args)


@mcp.tool()
def flow_login(profile_idx: int = 0) -> str:
    """프로필 로그인용 인터랙티브 기동(브라우저 열림 → 사용자가 로그인)."""
    return _run(["--profile-idx", str(profile_idx), "--interactive"], timeout=60)


if __name__ == "__main__":
    mcp.run()
