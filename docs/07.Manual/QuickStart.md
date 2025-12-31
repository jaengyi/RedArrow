# RedArrow 빠른 시작 가이드

## 📌 5분 안에 시작하기

이 문서는 경험 있는 사용자를 위한 빠른 시작 가이드입니다.
처음 사용하신다면 [ExecutionGuide.md](./ExecutionGuide.md)를 참고하세요.

---

## ⚡ 빠른 설치 및 실행

### 1단계: 프로젝트 클론 및 설정 (1분)

```bash
# 프로젝트 클론
git clone https://github.com/jaengyi/RedArrow.git
cd RedArrow

# Python 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: API 키 설정 (2분)

```bash
# .env 파일이 이미 있다면 이 단계 스킵
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 선호하는 에디터 사용
```

**필수 입력 항목:**
```env
TRADING_MODE=simulation

SIMULATION_APP_KEY=여기에_모의투자_APP_KEY_입력
SIMULATION_APP_SECRET=여기에_모의투자_APP_SECRET_입력
SIMULATION_ACCOUNT_NUMBER=여기에_모의투자_계좌번호_입력
```

### 3단계: 설정 검증 (30초)

```bash
python -m src.config.settings
```

**예상 출력:**
```
✅ 설정 검증 성공
```

### 4단계: 프로그램 실행 (즉시)

```bash
python src/main.py
```

---

## 🎯 체크리스트

실행 전 확인사항:

- [ ] Python 3.11 이상 설치됨
- [ ] 한국투자증권 API 키 발급받음
- [ ] `.env` 파일에 API 키 입력 완료
- [ ] 설정 검증 성공
- [ ] 시장 운영 시간 (평일 09:00-15:30)

---

## 🔄 모드 전환

### 모의투자 → 실전투자

```bash
# .env 파일 수정
TRADING_MODE=real

# 실전투자 API 키 확인
REAL_APP_KEY=실제_값_입력됨
REAL_APP_SECRET=실제_값_입력됨
REAL_ACCOUNT_NUMBER=실제_값_입력됨
```

⚠️ **실전투자는 실제 돈이 거래됩니다! 충분한 테스트 후 전환하세요.**

---

## 📊 모니터링

### 로그 실시간 확인

```bash
tail -f logs/redarrow.log
```

### 거래 내역 확인

```bash
grep "매수\|매도" logs/redarrow.log
```

---

## 🛑 프로그램 중지

```bash
# Ctrl + C 또는
kill -SIGTERM <PID>
```

---

## ⚙️ 주요 설정 변경

### 리스크 관리 조정

`.env` 파일에서 수정:

```env
STOP_LOSS_PERCENT=2.5       # 손절률
TAKE_PROFIT_PERCENT=5.0     # 익절률
MAX_POSITION_SIZE=1000000   # 단일 종목 최대 투자금
MAX_POSITIONS=5             # 최대 보유 종목 수
```

### 종목 선정 기준 조정

`config/config.yaml` 파일에서 수정:

```yaml
stock_selector:
  top_volume_count: 30          # 거래대금 상위 n개
  volume_surge_threshold: 2.0   # 거래량 폭증 기준 (배수)
  min_score: 5                  # 최소 선정 점수
```

---

## 🚨 긴급 대응

### 즉시 모든 포지션 청산

프로그램 중지 후:

```bash
# 수동으로 한국투자증권 앱/웹에서 청산
# 또는 긴급 청산 스크립트 실행 (구현 예정)
```

### 거래 일시 중지

```env
# .env에 추가
TRADING_ENABLED=false
```

---

## 📞 도움말

- **상세 가이드**: [ExecutionGuide.md](./ExecutionGuide.md)
- **문제 해결**: [TroubleShooting.md](./TroubleShooting.md)
- **API 키 관리**: [../06.Security/APIKeyManagement.md](../06.Security/APIKeyManagement.md)
- **데이터베이스**: [../06.Security/DatabaseGuide.md](../06.Security/DatabaseGuide.md)

---

## 📝 일일 운영 루틴

### 장 시작 전 (09:00 이전)

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 최신 코드 업데이트 (선택)
git pull

# 3. 프로그램 시작
python src/main.py
```

### 장 마감 후

```bash
# 1. 당일 거래 확인
grep "$(date +%Y-%m-%d)" logs/redarrow.log

# 2. 성과 요약 (수동)
grep "손익\|수익률" logs/redarrow.log | tail -10

# 3. 프로그램 종료 (자동 종료되지 않은 경우)
# Ctrl + C
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 빠른 시작 가이드 초안 작성 | - |
