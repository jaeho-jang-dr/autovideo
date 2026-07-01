# -*- coding: utf-8 -*-
import sys

# Unicode escape sequences for:
# '실행 중입니다.' -> '\uc2e4\ud589 \uc911\uc785\ub2c8\ub2e4.'
# '이미 실행 중' -> '\uc774\ubbf8 \uc2e4\ud589 \uc911'
# '오류가 발생' -> '\uc624\ub958\uac00 \ubc1c\uc0dd'
# '다른 사용자가' -> '\ub2e4\ub978 \uc0ac\uc6a9\uc790\uac00'
# '로그인' -> '\ub85c\uadf8\uc778'

words = {
    '실행 중입니다.': '\uc2e4\ud589 \uc911\uc785\ub2c8\ub2e4.',
    '이미 실행 중': '\uc774\ubbf8 \uc2e4\ud589 \uc911',
    '오류가 발생': '\uc624\ub958\uac00 \ubc1c\uc0dd',
    '다른 사용자가': '\ub2e4\ub978 \uc0ac\uc6a9\uc790\uac00',
    '로그인': '\ub85c\uadf8\uc778'
}

for name, s in words.items():
    try:
        b_utf8 = s.encode('utf-8')
        b_cp949 = s.encode('cp949')
        print(f"Original: {name}")
        print(f"  utf8 decoded as cp949: {b_utf8.decode('cp949', errors='replace')}")
        print(f"  cp949 decoded as utf8: {b_cp949.decode('utf-8', errors='replace')}")
    except Exception as e:
        print(f"Error for {name}: {e}")
