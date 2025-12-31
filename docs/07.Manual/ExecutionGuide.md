# RedArrow 실행 가이드

## 📚 문서 정보
- **작성일**: 2025-12-31
- **대상**: 처음 사용하는 사용자
- **난이도**: 초급
- **소요 시간**: 약 30분

---

## 목차

1. [사전 준비사항](#1-사전-준비사항)
2. [환경 설정](#2-환경-설정)
3. [API 키 설정](#3-api-키-설정)
4. [설정 파일 조정](#4-설정-파일-조정)
5. [프로그램 실행](#5-프로그램-실행)
6. [모니터링 및 관리](#6-모니터링-및-관리)
7. [프로그램 종료](#7-프로그램-종료)
8. [자동 실행 설정](#8-자동-실행-설정)

---

## 1. 사전 준비사항

### 1.1 필수 소프트웨어 확인

#### Python 버전 확인

```bash
python3 --version
```

**요구사항**: Python 3.11 이상

**설치되지 않은 경우:**

**macOS:**
```bash
# Homebrew 사용
brew install python@3.11
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
- Python 공식 사이트에서 다운로드: https://www.python.org/downloads/

#### Git 확인

```bash
git --version
```

**설치되지 않은 경우:**
```bash
# macOS
brew install git

# Ubuntu/Linux
sudo apt install git
```

### 1.2 한국투자증권 API 준비

1. **한국투자증권 계좌 개설**
   - 실전투자 또는 모의투자 계좌 필요

2. **API 키 발급**
   - 포털: https://apiportal.koreainvestment.com/
   - 로그인 후 "APP KEY 발급" 메뉴
   - **모의투자**와 **실전투자** 각각 발급 (권장)

3. **발급받을 정보**
   - APP_KEY (앱 키)
   - APP_SECRET (앱 시크릿)
   - 계좌번호

📝 **메모**: 발급받은 정보를 안전한 곳에 기록해두세요!

---

## 2. 환경 설정

### 2.1 프로젝트 다운로드

#### Git Clone 사용 (권장)

```bash
# 원하는 디렉토리로 이동
cd ~/projects  # 예시

# 프로젝트 클론
git clone https://github.com/jaengyi/RedArrow.git

# 프로젝트 디렉토리 진입
cd RedArrow
```

#### ZIP 다운로드 사용

1. GitHub 페이지에서 "Code" → "Download ZIP"
2. 압축 해제
3. 터미널에서 해당 폴더로 이동

```bash
cd ~/Downloads/RedArrow-main
```

### 2.2 프로젝트 구조 확인

```bash
ls -la
```

**예상 출력:**
```
.
├── .env.example          # 환경 변수 템플릿
├── .gitignore
├── README.md
├── config/
│   └── config.yaml       # 시스템 설정
├── docs/                 # 문서
├── logs/                 # 로그 디렉토리
├── requirements.txt      # Python 의존성
└── src/                  # 소스 코드
    ├── config/
    ├── indicators/
    ├── risk_manager/
    ├── stock_selector/
    └── main.py           # 메인 실행 파일
```

### 2.3 Python 가상환경 생성

가상환경을 사용하면 프로젝트별로 독립적인 Python 환경을 관리할 수 있습니다.

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux

# Windows의 경우
# venv\Scripts\activate
```

**활성화 확인:**
프롬프트 앞에 `(venv)`가 표시됩니다:
```
(venv) user@macbook RedArrow %
```

### 2.4 의존성 패키지 설치

```bash
# requirements.txt의 모든 패키지 설치
pip install -r requirements.txt
```

**설치 확인:**
```bash
pip list
```

**주요 패키지:**
- pandas
- numpy
- pyyaml
- python-dotenv
- requests

⏱️ **소요 시간**: 약 2-3분

---

## 3. API 키 설정

### 3.1 .env 파일 생성

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

### 3.2 .env 파일 편집

```bash
# 텍스트 에디터로 .env 파일 열기
nano .env

# 또는 VS Code 사용
code .env

# 또는 vi 사용
vi .env
```

### 3.3 필수 항목 입력

`.env` 파일에서 다음 항목을 수정하세요:

```env
# ========================================
# 증권사 API 설정
# ========================================

# 거래 모드: simulation (모의투자) 또는 real (실전투자)
TRADING_MODE=simulation

# ========================================
# 한국투자증권 - 모의투자 계정
# ========================================
SIMULATION_APP_KEY=여기에_발급받은_모의투자_APP_KEY_입력
SIMULATION_APP_SECRET=여기에_발급받은_모의투자_APP_SECRET_입력
SIMULATION_ACCOUNT_NUMBER=여기에_모의투자_계좌번호_입력

# ========================================
# 한국투자증권 - 실전투자 계정
# ========================================
REAL_APP_KEY=여기에_발급받은_실전투자_APP_KEY_입력
REAL_APP_SECRET=여기에_발급받은_실전투자_APP_SECRET_입력
REAL_ACCOUNT_NUMBER=여기에_실전투자_계좌번호_입력
```

**입력 예시 (가상의 데이터):**
```env
TRADING_MODE=simulation

SIMULATION_APP_KEY=PSxkN3fH8Gp2Lm9Rq4Tv7Yw1Zb5Cd8Ef
SIMULATION_APP_SECRET=xJ2kL9mP6qR3sT7vW1yZ5bC8dF4gH0jK...
SIMULATION_ACCOUNT_NUMBER=50123456-01
```

💡 **팁**: 처음에는 `TRADING_MODE=simulation`으로 시작하세요!

### 3.4 저장 및 종료

**nano 에디터:**
- `Ctrl + O` (저장)
- `Enter` (확인)
- `Ctrl + X` (종료)

**vi 에디터:**
- `Esc` → `:wq` → `Enter`

### 3.5 설정 검증

```bash
python -m src.config.settings
```

**성공 시 출력:**
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

⚠️  경고:
  - 데이터베이스 미설정 (현재는 사용하지 않음)

✅ 설정 검증 성공
```

**실패 시:**
- API 키가 올바르게 입력되었는지 확인
- 복사/붙여넣기 시 공백이 들어가지 않았는지 확인
- `docs/06.Security/APIKeyManagement.md` 참고

---

## 4. 설정 파일 조정

### 4.1 config.yaml 확인

```bash
cat config/config.yaml
```

### 4.2 주요 설정 항목

#### 리스크 관리

```yaml
risk_management:
  stop_loss_percent: 2.5        # 손절률 (%)
  take_profit_percent: 5.0      # 익절률 (%)
  trailing_stop: true           # 트레일링 스탑 사용
  trailing_stop_percent: 1.5    # 트레일링 스탑 비율
  max_position_size: 1000000    # 단일 종목 최대 투자금 (원)
  max_positions: 5              # 최대 보유 종목 수
  daily_loss_limit: -5.0        # 일일 최대 손실률 (%)
```

#### 종목 선정

```yaml
stock_selector:
  top_volume_count: 30              # 거래대금 상위 n개 종목
  volume_surge_threshold: 2.0       # 거래량 폭증 기준 (배수)
  min_score: 5                      # 최소 선정 점수
  k_value: 0.5                      # 변동성 돌파 K값
```

#### 시장 운영 시간

```yaml
market_hours:
  start: "09:00"
  end: "15:30"
  timezone: "Asia/Seoul"
```

### 4.3 설정 변경 (선택)

초기에는 기본값 사용을 권장하며, 필요시 수정:

```bash
nano config/config.yaml
```

---

## 5. 프로그램 실행

### 5.1 실행 전 체크리스트

- [ ] 가상환경 활성화됨 (`(venv)` 표시 확인)
- [ ] API 키 설정 완료
- [ ] 설정 검증 성공
- [ ] 시장 운영 시간 (평일 09:00-15:30)
- [ ] 인터넷 연결 확인

### 5.2 프로그램 실행

```bash
python src/main.py
```

### 5.3 실행 화면

**정상 시작 시:**
```
2025-12-31 09:00:00 [INFO] RedArrow 시스템 시작
2025-12-31 09:00:01 [INFO] 한국투자증권 API 연결 성공
2025-12-31 09:00:02 [INFO] 모의투자 모드로 실행 중
2025-12-31 09:00:03 [INFO] 시장 데이터 수집 중...
2025-12-31 09:00:05 [INFO] 거래대금 상위 30개 종목 필터링 완료
2025-12-31 09:00:06 [INFO] 종목 분석 시작...
```

**시장 시간 외:**
```
2025-12-31 20:00:00 [INFO] RedArrow 시스템 시작
2025-12-31 20:00:01 [WARNING] 시장 운영 시간이 아닙니다
2025-12-31 20:00:01 [INFO] 프로그램을 종료합니다
```

### 5.4 첫 거래 확인

종목이 선정되고 조건이 맞으면 자동으로 매수합니다:

```
2025-12-31 09:15:23 [INFO] 종목 선정: 삼성전자 (점수: 7점)
2025-12-31 09:15:24 [INFO] 매수 주문: 삼성전자 10주 @ 70,000원
2025-12-31 09:15:25 [INFO] 주문 체결 완료 (주문번호: 20251231-001)
```

---

## 6. 모니터링 및 관리

### 6.1 실시간 로그 모니터링

**다른 터미널 창 열기:**
```bash
cd /Users/hyoungwook.oh/projects/RedArrow
tail -f logs/redarrow.log
```

**특정 키워드만 보기:**
```bash
# 매수/매도만 보기
tail -f logs/redarrow.log | grep "매수\|매도"

# 에러만 보기
tail -f logs/redarrow.log | grep "ERROR"
```

### 6.2 당일 거래 내역 확인

```bash
# 오늘 날짜의 거래만 확인
grep "$(date +%Y-%m-%d)" logs/redarrow.log | grep "매수\|매도\|체결"
```

### 6.3 포지션 현황 확인

프로그램 실행 중 로그에서 확인:
```
2025-12-31 10:00:00 [INFO] 현재 포지션: 3개
2025-12-31 10:00:00 [INFO] - 삼성전자: +2.3% (70,000 → 71,610)
2025-12-31 10:00:00 [INFO] - SK하이닉스: +1.5% (120,000 → 121,800)
2025-12-31 10:00:00 [INFO] - NAVER: -0.8% (200,000 → 198,400)
```

### 6.4 손익 확인

```bash
# 손익 관련 로그만 확인
grep "손익\|수익률" logs/redarrow.log
```

### 6.5 시스템 리소스 모니터링

```bash
# CPU 및 메모리 사용량 확인
top -p $(pgrep -f "python src/main.py")

# 또는
htop  # htop이 설치된 경우
```

---

## 7. 프로그램 종료

### 7.1 정상 종료

프로그램이 실행 중인 터미널에서:

```bash
Ctrl + C
```

**종료 시 메시지:**
```
2025-12-31 15:30:00 [INFO] 종료 신호 수신
2025-12-31 15:30:01 [INFO] 현재 포지션 확인 중...
2025-12-31 15:30:02 [INFO] 미체결 주문 취소 중...
2025-12-31 15:30:03 [INFO] 종료 완료
```

### 7.2 강제 종료 (비권장)

```bash
# 프로세스 ID 확인
ps aux | grep "python src/main.py"

# 강제 종료
kill -9 <PID>
```

⚠️ **경고**: 강제 종료 시 미체결 주문이 처리되지 않을 수 있습니다.

### 7.3 종료 후 확인사항

1. **미체결 주문 확인**
   - 한국투자증권 앱/웹에서 확인

2. **보유 포지션 확인**
   - 의도하지 않은 포지션 보유 여부 확인

3. **로그 백업 (선택)**
   ```bash
   cp logs/redarrow.log logs/backup/redarrow_$(date +%Y%m%d).log
   ```

---

## 8. 자동 실행 설정

### 8.1 cron 사용 (Linux/macOS)

매일 장 시작 시 자동 실행:

```bash
# crontab 편집
crontab -e

# 다음 줄 추가 (평일 오전 8:55에 실행)
55 8 * * 1-5 cd /Users/hyoungwook.oh/projects/RedArrow && source venv/bin/activate && python src/main.py >> logs/cron.log 2>&1
```

### 8.2 systemd 사용 (Linux)

서비스 파일 생성:

```bash
sudo nano /etc/systemd/system/redarrow.service
```

내용:
```ini
[Unit]
Description=RedArrow Trading System
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/RedArrow
ExecStart=/home/yourusername/RedArrow/venv/bin/python src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable redarrow
sudo systemctl start redarrow
sudo systemctl status redarrow
```

### 8.3 macOS launchd 사용

Plist 파일 생성:

```bash
nano ~/Library/LaunchAgents/com.redarrow.trading.plist
```

내용:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.redarrow.trading</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/yourusername/RedArrow/venv/bin/python</string>
        <string>/Users/yourusername/RedArrow/src/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/yourusername/RedArrow</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>55</integer>
        <key>Weekday</key>
        <integer>1-5</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/yourusername/RedArrow/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/RedArrow/logs/launchd_error.log</string>
</dict>
</plist>
```

활성화:
```bash
launchctl load ~/Library/LaunchAgents/com.redarrow.trading.plist
```

---

## 9. 일일 운영 루틴

### 9.1 장 시작 전 (08:30 - 09:00)

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/hyoungwook.oh/projects/RedArrow

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 최신 코드 업데이트 (선택)
git pull

# 4. 설정 확인
python -m src.config.settings

# 5. 프로그램 시작
python src/main.py

# 6. 로그 모니터링 (다른 터미널)
tail -f logs/redarrow.log
```

### 9.2 장 중 (09:00 - 15:30)

- 로그 모니터링으로 시스템 상태 확인
- 이상 징후 발견 시 즉시 대응
- 급격한 시장 변동 시 수동 개입 고려

### 9.3 장 마감 후 (15:30 이후)

```bash
# 1. 당일 거래 내역 확인
grep "$(date +%Y-%m-%d)" logs/redarrow.log | grep "체결"

# 2. 손익 확인
grep "$(date +%Y-%m-%d)" logs/redarrow.log | grep "손익"

# 3. 보유 포지션 확인
# 한국투자증권 앱/웹에서 확인

# 4. 로그 백업
cp logs/redarrow.log logs/backup/redarrow_$(date +%Y%m%d).log

# 5. 프로그램 종료 (아직 실행 중이면)
# Ctrl + C
```

---

## 10. 모드 전환 가이드

### 10.1 모의투자 → 실전투자 전환

⚠️ **중요**: 실전투자는 실제 돈이 거래됩니다!

**전환 전 체크리스트:**
- [ ] 모의투자에서 충분히 테스트 (최소 1주일 권장)
- [ ] 전략의 수익률 확인
- [ ] 리스크 관리 검증
- [ ] 실전투자 API 키 발급 완료
- [ ] 실전투자 계좌에 충분한 자금 입금

**전환 절차:**

1. **프로그램 중지**
   ```bash
   Ctrl + C
   ```

2. **.env 파일 수정**
   ```bash
   nano .env
   ```

   ```env
   # 모드 변경
   TRADING_MODE=real

   # 실전투자 API 키 확인
   REAL_APP_KEY=실제_값_입력됨
   REAL_APP_SECRET=실제_값_입력됨
   REAL_ACCOUNT_NUMBER=실제_값_입력됨
   ```

3. **설정 검증**
   ```bash
   python -m src.config.settings
   ```

   **확인:**
   ```
   거래 모드: real
   모의투자: False
   ```

4. **신중하게 재시작**
   ```bash
   python src/main.py
   ```

5. **첫 거래 면밀히 모니터링**

---

## 📞 도움말 및 추가 정보

### 관련 문서

- **빠른 시작**: [QuickStart.md](./QuickStart.md)
- **문제 해결**: [TroubleShooting.md](./TroubleShooting.md)
- **API 키 관리**: [../06.Security/APIKeyManagement.md](../06.Security/APIKeyManagement.md)
- **시스템 설계**: [../03.Design/SystemDesign_20251231.md](../03.Design/SystemDesign_20251231.md)

### 추가 지원

- **GitHub Issues**: https://github.com/jaengyi/RedArrow/issues
- **문서**: `docs/` 디렉토리의 모든 문서 참고

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 실행 가이드 초안 작성 | - |
