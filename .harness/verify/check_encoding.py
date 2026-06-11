"""
.harness/verify/check_encoding.py
모든 지정 파일의 UTF-8 인코딩 및 BOM 자동 검사

사용법:
  python .harness/verify/check_encoding.py           # *.html 검사
  python .harness/verify/check_encoding.py --fix     # BOM 자동 제거
  python .harness/verify/check_encoding.py --pattern "*.py"
"""
import sys, os, glob, argparse
sys.stdout.reconfigure(encoding='utf-8')

def check_file(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    has_bom = raw[:3] == b'\xef\xbb\xbf'
    try:
        (raw[3:] if has_bom else raw).decode('utf-8')
        return has_bom, True, len(raw)
    except UnicodeDecodeError:
        return has_bom, False, len(raw)

def fix_bom(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'\xef\xbb\xbf':
        content = raw[3:].decode('utf-8')
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fix', action='store_true')
    parser.add_argument('--pattern', default='*.html')
    parser.add_argument('--path', default='.')
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.path, args.pattern)))
    if not files:
        print(f'검사할 파일 없음: {args.pattern}')
        sys.exit(0)

    total = bom_count = error_count = fixed_count = 0
    print(f'\n{"="*60}')
    print(f'  인코딩 검사 — {len(files)}개 파일 ({args.pattern})')
    print(f'{"="*60}')

    for fp in files:
        total += 1
        name = os.path.basename(fp)
        has_bom, is_utf8, size = check_file(fp)
        if has_bom:
            bom_count += 1
            status = '❌ BOM 발견'
            if args.fix:
                fix_bom(fp)
                fixed_count += 1
                status += ' → 수정완료'
        elif not is_utf8:
            error_count += 1
            status = '⚠️  UTF-8 아님'
        else:
            status = '✅ 정상'
        print(f'  {name:<50} {status}  ({size/1024:.1f}KB)')

    print(f'{"="*60}')
    print(f'  총 {total}개 | BOM: {bom_count}개 | 오류: {error_count}개')
    if args.fix and fixed_count:
        print(f'  수정: {fixed_count}개')
    print(f'{"="*60}\n')
    if bom_count == 0 and error_count == 0:
        sys.exit(0)
    if not args.fix:
        print('  💡 수정: python .harness/verify/check_encoding.py --fix')
    sys.exit(1)

if __name__ == '__main__':
    main()
