# RedArrow - 단기투자 종목 선정 시스템

단기투자(단타 및 스캘핑)를 위한 자동 종목 선정 프로그램입니다.

## 주요 기능

### 1. 실시간 데이터 수집
- 거래대금 상위 종목 모니터링 (20~30위권)
- 실시간 주가 등락률 추적
- 분봉 데이터 수집 (1분, 3분, 5분)
- 호가창 데이터 (잔량 및 체결 속도)
- 테마/섹터 그룹 정보
- 뉴스 및 공시 키워드 감지

### 2. 기술적 지표 분석
- 이동평균선 (5일, 20일, 분봉 20분/60분)
- 변동성 돌파 지표 (K-값 = 0.5)
- MACD (추세 전환 감지)
- 스토캐스틱 (과매도/과매수 판단)
- OBV (거래량 분석)

### 3. 종목 선정 신호 감지
- 거래량 폭증 (평소 대비 2~5배)
- 호가창 불균형
- VI 발동 감지
- 섹터 동조화 현상
- 눌림목 형성

### 4. 리스크 관리
- 자동 손절 설정 (-2~3% 또는 이동평균선 이탈)
- 오버나이트 여부 자동 결정

---

## 필수 준비사항

### 1. 증권사 API 선택 및 가입

아래 증권사 중 **하나를 선택**하여 API 사용 신청이 필요합니다:

#### 옵션 1: 한국투자증권 Open API (권장)
- **신청 방법**:
  1. 한국투자증권 계좌 개설
  2. API 포털 접속: https://apiportal.koreainvestment.com/
  3. 앱 등록 및 API Key 발급
- **필요 정보**:
  - APP_KEY (앱 키)
  - APP_SECRET (앱 시크릿)
  - ACCOUNT_NUMBER (계좌번호)
  - 모의투자/실전투자 선택
- **장점**: 안정적, 문서화 우수, REST API 제공

#### 옵션 2: 키움증권 Open API
- **신청 방법**:
  1. 키움증권 계좌 개설
  2. OpenAPI 다운로드: https://www.kiwoom.com/
  3. API 사용 신청
- **필요 정보**:
  - 계좌번호
  - 계좌비밀번호
- **참고**: Windows 전용 (ActiveX 기반)

#### 옵션 3: 이베스트투자증권 xingAPI
- **신청 방법**:
  1. 이베스트투자증권 계좌 개설
  2. xingAPI 신청
- **필요 정보**:
  - 사용자 ID
  - 계좌번호
  - 인증서

### 2. 데이터베이스 설치

#### PostgreSQL (과거 데이터 저장)
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Linux
sudo apt-get install postgresql-15
sudo systemctl start postgresql
```

**데이터베이스 생성**:
```bash
createdb redarrow_db
```

**필요 정보**:
- DB_HOST (기본: localhost)
- DB_PORT (기본: 5432)
- DB_NAME (예: redarrow_db)
- DB_USER
- DB_PASSWORD

#### Redis (실시간 데이터 캐싱)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

**필요 정보**:
- REDIS_HOST (기본: localhost)
- REDIS_PORT (기본: 6379)

### 3. TA-Lib 설치

기술적 지표 계산을 위한 TA-Lib 라이브러리 설치:

```bash
# macOS
brew install ta-lib

# Ubuntu/Linux
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

---

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/RedArrow.git
cd RedArrow
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성:

```env
# 증권사 API 설정 (한국투자증권 예시)
BROKER_TYPE=koreainvestment
APP_KEY=your_app_key_here
APP_SECRET=your_app_secret_here
ACCOUNT_NUMBER=your_account_number
TRADING_MODE=simulation  # simulation 또는 real

# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=redarrow_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379

# 리스크 관리 설정
STOP_LOSS_PERCENT=2.5  # 손절 기준 (%)
MAX_POSITION_SIZE=1000000  # 단일 종목 최대 투자금 (원)
```

### 5. 설정 파일 편집

`config/config.yaml` 파일을 확인하고 필요시 수정:

```yaml
stock_selector:
  top_volume_count: 30  # 거래대금 상위 종목 수
  volume_surge_threshold: 2.0  # 거래량 폭증 기준 (배수)
  ma_periods:
    short: 5
    medium: 20
  k_value: 0.5  # 변동성 돌파 K값

indicators:
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9
  stochastic:
    k_period: 14
    d_period: 3
    oversold: 20
    overbought: 80

risk_management:
  stop_loss_percent: 2.5
  trailing_stop: true
  overnight_hold: false  # 오버나이트 여부
```

---

## 사용 방법

### 프로그램 실행
```bash
python src/main.py
```

### 시뮬레이션 모드 실행
```bash
# .env 파일에서 TRADING_MODE=simulation 설정 후
python src/main.py
```

### 실전 거래 모드 (주의!)
```bash
# .env 파일에서 TRADING_MODE=real 설정 후
python src/main.py
```

---

## 프로젝트 구조

```
RedArrow/
├── src/
│   ├── config/              # 설정 관리
│   │   └── settings.py
│   ├── data_collectors/     # 데이터 수집
│   │   └── broker_api.py    # 증권사 API 연동
│   ├── indicators/          # 기술적 지표
│   │   └── technical_indicators.py
│   ├── stock_selector/      # 종목 선정
│   │   └── selector.py
│   ├── risk_manager/        # 리스크 관리
│   │   └── risk_control.py
│   └── main.py              # 메인 실행 파일
├── config/
│   └── config.yaml          # 설정 파일
├── docs/                    # 문서
├── .env                     # 환경 변수 (직접 생성)
├── requirements.txt         # 의존성
└── README.md
```

---

## 주요 클래스 및 모듈

### StockSelector
종목 선정 로직을 담당하는 핵심 클래스

**주요 메서드**:
- `get_top_volume_stocks()`: 거래대금 상위 종목 조회
- `detect_volume_surge()`: 거래량 폭증 감지
- `check_ma_breakout()`: 이동평균선 돌파 확인
- `detect_vi_trigger()`: VI 발동 감지
- `select_stocks()`: 종목 선정 실행

### TechnicalIndicators
기술적 지표 계산

**주요 메서드**:
- `calculate_ma()`: 이동평균선
- `calculate_macd()`: MACD
- `calculate_stochastic()`: 스토캐스틱
- `calculate_obv()`: OBV
- `calculate_volatility_breakout()`: 변동성 돌파

### RiskManager
리스크 관리

**주요 메서드**:
- `check_stop_loss()`: 손절 기준 확인
- `check_overnight_eligibility()`: 오버나이트 여부 판단
- `calculate_position_size()`: 포지션 크기 계산

---

## 로그 및 모니터링

프로그램 실행 시 `logs/` 디렉토리에 로그 파일이 생성됩니다:
- `redarrow_YYYYMMDD.log`: 일별 로그
- `error_YYYYMMDD.log`: 에러 로그

---

## 주의사항

1. **실전 거래 전 충분한 테스트**: 반드시 시뮬레이션 모드로 충분히 테스트 후 실전 거래를 진행하세요.
2. **API 키 보안**: `.env` 파일은 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함됨).
3. **리스크 관리**: 자동 손절 설정을 반드시 활성화하세요.
4. **시장 개장 시간**: 프로그램은 한국 주식시장 개장 시간(09:00~15:30)에 실행됩니다.

---

## 라이선스

MIT License

---

## 면책 조항

본 프로그램은 교육 및 연구 목적으로 제공됩니다. 실제 투자에 사용 시 발생하는 손실에 대해 개발자는 책임지지 않습니다. 투자는 본인의 판단과 책임 하에 진행하시기 바랍니다.
