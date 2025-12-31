# API 키 관리 가이드

## 📌 개요

한국투자증권에서 발급받은 API 키를 안전하게 관리하고 사용하는 방법을 설명합니다.

---

## 🔑 API 키 저장 위치

### 1. `.env` 파일에 저장

프로젝트 루트 디렉토리의 **`.env`** 파일에 API 키를 저장합니다.

```bash
/Users/hyoungwook.oh/projects/RedArrow/.env
```

**⚠️ 중요:**
- 이 파일은 `.gitignore`에 등록되어 있어 Github에 절대 업로드되지 않습니다.
- 절대 다른 사람과 공유하지 마세요!

---

## 📝 API 키 입력 방법

`.env` 파일을 열고 아래 항목을 수정하세요:

### 1. 모의투자 계정 정보 입력

```env
# ========================================
# 한국투자증권 - 모의투자 계정
# ========================================
SIMULATION_APP_KEY=실제_모의투자_APP_KEY를_여기에_붙여넣기
SIMULATION_APP_SECRET=실제_모의투자_APP_SECRET을_여기에_붙여넣기
SIMULATION_ACCOUNT_NUMBER=실제_모의투자_계좌번호를_여기에_입력
```

### 2. 실전투자 계정 정보 입력

```env
# ========================================
# 한국투자증권 - 실전투자 계정
# ========================================
REAL_APP_KEY=실제_실전투자_APP_KEY를_여기에_붙여넣기
REAL_APP_SECRET=실제_실전투자_APP_SECRET을_여기에_붙여넣기
REAL_ACCOUNT_NUMBER=실제_실전투자_계좌번호를_여기에_입력
```

### 3. 거래 모드 선택

```env
# 거래 모드: simulation (모의투자) 또는 real (실전투자)
TRADING_MODE=simulation
```

**모드 설명:**
- `TRADING_MODE=simulation`: 모의투자 계정 사용 (안전하게 테스트)
- `TRADING_MODE=real`: 실전투자 계정 사용 (실제 돈으로 거래)

---

## 🔄 자동 계정 전환

시스템은 `TRADING_MODE` 설정에 따라 자동으로 올바른 API 키를 선택합니다:

| TRADING_MODE | 사용되는 API 키 | 사용되는 계좌 |
|--------------|-----------------|---------------|
| `simulation` | SIMULATION_APP_KEY<br>SIMULATION_APP_SECRET | SIMULATION_ACCOUNT_NUMBER |
| `real` | REAL_APP_KEY<br>REAL_APP_SECRET | REAL_ACCOUNT_NUMBER |

**코드 수정 없이** `.env` 파일의 `TRADING_MODE`만 변경하면 즉시 적용됩니다!

---

## 📋 입력 예시

### 실제 입력 예시 (가상의 데이터)

```env
# ========================================
# 한국투자증권 - 모의투자 계정
# ========================================
SIMULATION_APP_KEY=PSxkN3fH8Gp2Lm9Rq4Tv7Yw1Zb5Cd8Ef
SIMULATION_APP_SECRET=xJ2kL9mP6qR3sT7vW1yZ5bC8dF4gH0jK
SIMULATION_ACCOUNT_NUMBER=50123456-01

# ========================================
# 한국투자증권 - 실전투자 계정
# ========================================
REAL_APP_KEY=Ax7Bw9Cy2Dz5Ef8Gh1Ij4Kl7Mn0Pq3Rs
REAL_APP_SECRET=uV6wX9yA2bC5dE8fG1hI4jK7lM0nO3pQ
REAL_ACCOUNT_NUMBER=12345678-01
```

---

## 🛡️ 보안 가이드

### ✅ 해야 할 것

1. **`.env` 파일 권한 설정** (Linux/macOS)
   ```bash
   chmod 600 .env
   ```
   - 파일 소유자만 읽기/쓰기 가능하도록 설정

2. **정기적인 키 재발급**
   - 보안을 위해 3~6개월마다 API 키를 재발급하는 것을 권장

3. **백업**
   - API 키를 안전한 곳(비밀번호 관리자 등)에 별도 백업

### ❌ 하지 말아야 할 것

1. **절대 Github에 업로드하지 마세요**
   - `.env` 파일은 이미 `.gitignore`에 등록됨
   - `git status`로 확인: `.env`가 나타나면 안 됨

2. **스크린샷 공유 금지**
   - API 키가 포함된 화면을 캡처하여 공유하지 마세요

3. **슬랙/카카오톡 등으로 전송 금지**
   - 절대 메신저로 API 키를 주고받지 마세요

4. **하드코딩 금지**
   - 소스 코드에 직접 API 키를 적지 마세요
   ```python
   # ❌ 나쁜 예
   app_key = "PSxkN3fH8Gp2Lm9Rq4Tv7Yw1Zb5Cd8Ef"

   # ✅ 좋은 예
   app_key = os.getenv('SIMULATION_APP_KEY')
   ```

---

## 🔍 검증 방법

API 키가 올바르게 설정되었는지 확인:

```bash
cd /Users/hyoungwook.oh/projects/RedArrow
python -m src.config.settings
```

**예상 출력:**
```
==================================================
RedArrow 설정 요약
==================================================
증권사: koreainvestment
거래 모드: simulation
모의투자: True
계좌번호: 50123456-01

손절률: 2.5%
익절률: 5.0%
최대 포지션: 5개
단일 종목 최대 투자금: 1,000,000원
==================================================

✅ 설정 검증 성공
```

**오류가 발생하면:**
```
❌ 설정 검증 실패:
  - APP_KEY가 설정되지 않았습니다.
  - APP_SECRET이 설정되지 않았습니다.

💡 .env 파일을 확인하고 필수 값을 입력하세요.
```

---

## 🔄 모드 전환 방법

### 모의투자 → 실전투자 전환

1. `.env` 파일 열기
2. `TRADING_MODE` 변경:
   ```env
   # Before
   TRADING_MODE=simulation

   # After
   TRADING_MODE=real
   ```
3. 프로그램 재시작

**⚠️ 주의:**
- 실전투자 모드에서는 실제 돈이 거래됩니다!
- 충분한 테스트 후에만 실전 모드로 전환하세요!

---

## 📞 문제 해결

### Q1. API 키가 없어요!

**A:** 한국투자증권 API 포털에서 발급받으세요:
- URL: https://apiportal.koreainvestment.com/
- 모의투자와 실전투자 각각 별도 발급

### Q2. `.env` 파일이 안 보여요!

**A:** 숨김 파일이라 안 보일 수 있습니다:

**macOS/Linux:**
```bash
ls -la | grep .env
```

**파인더에서 보기:**
- `Cmd + Shift + .` (점) 누르면 숨김 파일 표시

### Q3. Git에 `.env`가 올라갈까 봐 걱정돼요!

**A:** 안심하세요! 확인 방법:

```bash
# .gitignore에 등록되어 있는지 확인
cat .gitignore | grep ".env"

# Git 추적 파일 목록 확인 (.env가 없어야 정상)
git ls-files | grep ".env"
```

### Q4. 실수로 Github에 API 키를 올렸어요!

**A:** 즉시 조치:
1. 한국투자증권 포털에서 즉시 API 키 폐기
2. 새로운 API 키 재발급
3. Github에서 해당 커밋 삭제:
   ```bash
   # 히스토리에서 완전히 제거
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```

---

## 📚 관련 문서

- [한국투자증권 API 가이드](https://apiportal.koreainvestment.com/)
- [DeploymentGuide_20251231.md](../05.Deploy/DeploymentGuide_20251231.md) - 배포 시 환경 변수 관리
- [SystemDesign_20251231.md](../03.Design/SystemDesign_20251231.md) - 시스템 보안 설계

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | API 키 관리 가이드 초안 작성 | - |
