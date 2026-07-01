import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = "scratch/grammar_sources/src_23_한글한국어 교육 커리큘럼 수립을 위한 계통적 문법론 및 종합 어문 규범 소스 아카이브.md"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"File size: {len(content)} chars")
        print(content[:3000])
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
