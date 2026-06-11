# 재사용 패턴 카탈로그

## 패턴 1: 인코딩 안전 파일 저장

```python
# 항상 이 방식으로
with open('target.html', 'w', encoding='utf-8', newline='') as f:
    f.write(content)

# 절대 금지
# Set-Content -Encoding UTF8  (PowerShell — BOM 포함!)
```

---

## 패턴 2: 인코딩 복구

```python
# .harness/skills/encoding_fix.py 실행
python .harness/skills/encoding_fix.py

# 특정 파일만
python .harness/skills/encoding_fix.py --file target.html
```

---

## 패턴 3: 배포

```bash
# 1. 검증
python .harness/verify/check_encoding.py
python .harness/verify/check_links.py

# 2. 배포 (프로젝트별 명령어로 교체)
git add . && git commit -m "message" && git push
```

---

## 패턴 4: git 복원

```bash
# 특정 커밋의 파일 복원
git show <commit-hash>:target_file > target_file
```

---

## 패턴 5: Claude Code 위임

```
claude --dangerously-skip-permissions -p "
[작업 목표]: ...
[성공 기준]: ...
[제약 조건]: UTF-8, 테스트 통과
"
```

---

## TODO: 프로젝트 전용 패턴 추가

이 파일을 프로젝트에 맞는 패턴으로 채우세요.
