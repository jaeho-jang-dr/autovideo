import re
import os

astro_path = r"web/src/components/GrooveBoard.astro"
helper_path = r"scratch/replace_style.py"

print("Current directory:", os.getcwd())
print("Astro path exists:", os.path.exists(astro_path))
print("Helper path exists:", os.path.exists(helper_path))

with open(astro_path, "r", encoding="utf-8") as f:
    astro_content = f.read()

with open(helper_path, "r", encoding="utf-8") as f:
    helper_content = f.read()

# 정규식으로 scratch/replace_style.py에서 new_css 안의 <style>...</style> 추출
css_pattern = re.compile(r'new_css = """(<style>.*?</style>)"""', re.DOTALL)
match_css = css_pattern.search(helper_content)

if not match_css:
    print("CSS block not found in helper!")
else:
    new_css = match_css.group(1)
    print("New CSS block size:", len(new_css))
    
    # Astro 파일 내 style block 매칭
    astro_pattern = re.compile(r"<style>.*?</style>", re.DOTALL)
    matches = astro_pattern.findall(astro_content)
    print("Astro file style matches count:", len(matches))
    
    if len(matches) == 1:
        updated = astro_pattern.sub(new_css, astro_content)
        with open(astro_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print("Successfully replaced and written style block!")
    else:
        print("Cannot replace style, matches count is not 1!")
