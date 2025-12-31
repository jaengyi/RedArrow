# RedArrow - 프로그램 목록

## 문서 정보
- **작성일**: 2025-12-31
- **최종 수정일**: 2025-12-31
- **버전**: 1.0
- **작성자**: RedArrow Team

---

## 1. 프로그램 목록 개요

본 문서는 RedArrow 시스템을 구성하는 모든 프로그램(모듈, 클래스, 함수)의 목록과 개요를 기술합니다.

---

## 2. 디렉토리 구조

```
RedArrow/
├── src/                          # 소스 코드 디렉토리
│   ├── __init__.py              # 패키지 초기화 파일
│   ├── main.py                  # 메인 실행 파일
│   ├── config/                  # 설정 관리 모듈
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── data_collectors/         # 데이터 수집 모듈
│   │   ├── __init__.py
│   │   └── broker_api.py
│   ├── indicators/              # 기술적 지표 모듈
│   │   ├── __init__.py
│   │   └── technical_indicators.py
│   ├── stock_selector/          # 종목 선정 모듈
│   │   ├── __init__.py
│   │   └── selector.py
│   └── risk_manager/            # 리스크 관리 모듈
│       ├── __init__.py
│       └── risk_control.py
├── config/                      # 설정 파일 디렉토리
│   └── config.yaml
├── docs/                        # 문서 디렉토리
├── logs/                        # 로그 디렉토리 (런타임 생성)
├── .env                         # 환경 변수 (사용자 생성)
├── .env.example                 # 환경 변수 템플릿
├── .gitignore                   # Git 제외 목록
├── requirements.txt             # 의존성 목록
└── README.md                    # 프로젝트 README
```

---

## 3. 프로그램 목록

### 3.1 메인 프로그램

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| M-001 | main.py | src/main.py | 시스템 메인 실행 파일 |

#### M-001: main.py
- **목적**: 시스템 전체 실행 및 제어
- **주요 클래스**: RedArrowSystem
- **주요 함수**: main(), setup_logging()
- **의존성**: 모든 모듈

---

### 3.2 설정 관리 모듈 (config/)

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| C-001 | settings.py | src/config/settings.py | 설정 관리 클래스 |

#### C-001: settings.py
- **목적**: 환경 변수 및 YAML 설정 로드 및 관리
- **주요 클래스**: Settings
- **주요 메서드**:
  - `__init__(config_path)`: 설정 초기화
  - `validate()`: 설정 검증
  - `print_summary()`: 설정 요약 출력
  - 각종 프로퍼티: broker_type, db_config, redis_config 등

---

### 3.3 데이터 수집 모듈 (data_collectors/)

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| D-001 | broker_api.py | src/data_collectors/broker_api.py | 증권사 API 연동 인터페이스 |

#### D-001: broker_api.py
- **목적**: 증권사 API 연동 추상화 및 구현
- **주요 클래스**:
  - `BrokerAPI` (추상 클래스): API 인터페이스 정의
  - `KoreaInvestmentAPI`: 한국투자증권 API 구현
- **주요 메서드**:
  - `connect()`: API 연결
  - `disconnect()`: 연결 해제
  - `get_top_volume_stocks()`: 거래대금 상위 종목 조회
  - `get_stock_price()`: 개별 종목 현재가 조회
  - `get_historical_data()`: 과거 가격 데이터 조회
  - `get_minute_data()`: 분봉 데이터 조회
  - `get_order_book()`: 호가창 데이터 조회
  - `place_buy_order()`: 매수 주문
  - `place_sell_order()`: 매도 주문
  - `get_account_balance()`: 계좌 잔고 조회
  - `get_positions()`: 보유 종목 조회
- **주요 함수**:
  - `create_broker_api()`: API 팩토리 함수
- **참고**: 현재 템플릿 상태, 실제 구현 필요

---

### 3.4 기술적 지표 모듈 (indicators/)

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| I-001 | technical_indicators.py | src/indicators/technical_indicators.py | 기술적 지표 계산 |

#### I-001: technical_indicators.py
- **목적**: 다양한 기술적 지표 계산 제공
- **주요 클래스**: TechnicalIndicators
- **주요 메서드**:
  - **이동평균**:
    - `calculate_ma(data, period)`: 단순 이동평균
    - `calculate_ema(data, period)`: 지수 이동평균
  - **추세 지표**:
    - `calculate_macd(data, fast, slow, signal)`: MACD
    - `calculate_bollinger_bands(data, period, num_std)`: 볼린저 밴드
  - **모멘텀 지표**:
    - `calculate_stochastic(high, low, close, k, d)`: 스토캐스틱
    - `calculate_rsi(data, period)`: RSI
  - **거래량 지표**:
    - `calculate_obv(close, volume)`: OBV
  - **변동성 지표**:
    - `calculate_volatility_breakout(open, prev_high, prev_low, k)`: 변동성 돌파
  - **패턴 감지**:
    - `detect_golden_cross(short_ma, long_ma)`: 골든크로스
    - `detect_dead_cross(short_ma, long_ma)`: 데드크로스
    - `check_price_above_ma(price, ma_values)`: 이동평균선 상방 확인

---

### 3.5 종목 선정 모듈 (stock_selector/)

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| S-001 | selector.py | src/stock_selector/selector.py | 종목 선정 로직 |

#### S-001: selector.py
- **목적**: 기술적 지표 기반 종목 선정
- **주요 클래스**: StockSelector
- **주요 메서드**:
  - **필터링**:
    - `filter_by_volume_amount(stock_data, top_n)`: 거래대금 상위 필터링
  - **신호 감지**:
    - `detect_volume_surge(current_volume, avg_volume)`: 거래량 폭증
    - `check_ma_breakout(price_data, current_price)`: 이동평균 돌파
    - `check_golden_cross(price_data)`: 골든크로스 발생
    - `check_volatility_breakout(open, prev_high, prev_low, current)`: 변동성 돌파
  - **지표 신호**:
    - `check_macd_signal(price_data)`: MACD 매수/매도 신호
    - `check_stochastic_signal(high, low, close)`: 스토캐스틱 신호
    - `check_obv_trend(close, volume)`: OBV 추세
  - **패턴 분석**:
    - `detect_order_book_imbalance(bid_volume, ask_volume)`: 호가창 불균형
    - `detect_support_at_ma(price_data, current_price)`: 눌림목 형성
  - **메인 로직**:
    - `select_stocks(stock_data, price_history)`: 종목 선정 실행
- **알고리즘**: 점수 기반 선정 (최소 5점)

---

### 3.6 리스크 관리 모듈 (risk_manager/)

| 번호 | 프로그램명 | 파일 경로 | 설명 |
|------|-----------|----------|------|
| R-001 | risk_control.py | src/risk_manager/risk_control.py | 리스크 관리 |

#### R-001: risk_control.py
- **목적**: 손익 관리 및 포지션 제어
- **주요 클래스**: RiskManager
- **주요 메서드**:
  - **손익 관리**:
    - `check_stop_loss(entry, current, ma)`: 손절 확인
    - `check_take_profit(entry, current)`: 익절 확인
    - `calculate_trailing_stop(entry, highest, current)`: 트레일링 스톱
  - **포지션 관리**:
    - `calculate_position_size(price, balance, risk_percent)`: 포지션 크기 계산
    - `check_max_positions(current_positions)`: 최대 포지션 수 확인
  - **전략 관리**:
    - `check_overnight_eligibility(entry, current, market_status)`: 오버나이트 판단
    - `check_daily_loss_limit(daily_pnl, balance)`: 일일 손실 제한
  - **종합 판단**:
    - `should_close_position(entry, current, highest, ...)`: 청산 여부 판단

---

## 4. 설정 파일

### 4.1 YAML 설정 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| CF-001 | config.yaml | config/config.yaml | 프로그램 설정 |

#### CF-001: config.yaml
- **목적**: 시스템 동작 파라미터 정의
- **주요 섹션**:
  - `stock_selector`: 종목 선정 설정
  - `indicators`: 기술적 지표 파라미터
  - `risk_management`: 리스크 관리 설정
  - `market_hours`: 시장 운영 시간
  - `data_collection`: 데이터 수집 설정
  - `logging`: 로깅 설정
  - `notifications`: 알림 설정

### 4.2 환경 변수 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| CF-002 | .env | .env | 환경 변수 (사용자 생성) |
| CF-003 | .env.example | .env.example | 환경 변수 템플릿 |

#### CF-002, CF-003: .env, .env.example
- **목적**: API 키, DB 정보 등 민감 정보 관리
- **주요 변수**:
  - 증권사 API: BROKER_TYPE, APP_KEY, APP_SECRET, ACCOUNT_NUMBER
  - 데이터베이스: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  - Redis: REDIS_HOST, REDIS_PORT
  - 리스크: STOP_LOSS_PERCENT, MAX_POSITION_SIZE

---

## 5. 의존성 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| DP-001 | requirements.txt | requirements.txt | Python 패키지 의존성 |

#### DP-001: requirements.txt
- **목적**: 필수 Python 패키지 정의
- **주요 패키지**:
  - 데이터 처리: numpy, pandas
  - 기술적 지표: ta-lib, TA-Lib
  - 데이터베이스: redis, psycopg2-binary
  - API: requests, websocket-client, aiohttp
  - 설정: PyYAML, python-dotenv
  - 로깅: loguru
  - 스케줄링: APScheduler

---

## 6. 초기화 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| IN-001 | src/__init__.py | src/__init__.py | 루트 패키지 초기화 |
| IN-002 | config/__init__.py | src/config/__init__.py | 설정 모듈 초기화 |
| IN-003 | data_collectors/__init__.py | src/data_collectors/__init__.py | 데이터 수집 모듈 초기화 |
| IN-004 | indicators/__init__.py | src/indicators/__init__.py | 지표 모듈 초기화 |
| IN-005 | stock_selector/__init__.py | src/stock_selector/__init__.py | 선정 모듈 초기화 |
| IN-006 | risk_manager/__init__.py | src/risk_manager/__init__.py | 리스크 모듈 초기화 |

---

## 7. 문서 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| DOC-001 | README.md | README.md | 프로젝트 README |
| DOC-002 | Requirements_20251231.md | docs/01.Requirement/ | 요구사항 문서 |
| DOC-003 | TechnicalAnalysis_20251231.md | docs/02.Analysis/ | 기술 분석 문서 |
| DOC-004 | NotebookLM_20251231.pdf | docs/02.Analysis/ | 종목 선정 로직 |
| DOC-005 | SystemDesign_20251231.md | docs/03.Design/ | 시스템 설계서 |
| DOC-006 | ProgramList_20251231.md | docs/04.Implement/ | 프로그램 목록 (본 문서) |

---

## 8. Git 관련 파일

| 번호 | 파일명 | 경로 | 설명 |
|------|--------|------|------|
| GIT-001 | .gitignore | .gitignore | Git 제외 목록 |

---

## 9. 프로그램 통계

### 9.1 파일 통계
- **총 Python 파일**: 13개
- **총 설정 파일**: 3개
- **총 문서 파일**: 6개
- **총 라인 수**: 약 2,800줄

### 9.2 모듈별 통계

| 모듈 | 파일 수 | 클래스 수 | 함수/메서드 수 |
|------|---------|-----------|---------------|
| config | 1 | 1 | 20+ |
| data_collectors | 1 | 2 | 12 |
| indicators | 1 | 1 | 15 |
| stock_selector | 1 | 1 | 12 |
| risk_manager | 1 | 1 | 8 |
| main | 1 | 1 | 10 |
| **합계** | **6** | **7** | **77+** |

---

## 10. 프로그램 의존성 맵

```
main.py
  ├── config/settings.py
  ├── indicators/technical_indicators.py
  ├── stock_selector/selector.py
  │   └── indicators/technical_indicators.py
  ├── risk_manager/risk_control.py
  └── data_collectors/broker_api.py

config/settings.py
  ├── PyYAML
  └── python-dotenv

indicators/technical_indicators.py
  ├── numpy
  └── pandas

stock_selector/selector.py
  ├── pandas
  ├── numpy
  └── indicators/technical_indicators.py

risk_manager/risk_control.py
  └── pandas

data_collectors/broker_api.py
  ├── pandas
  └── requests (선택)
```

---

## 11. 프로그램 실행 순서

1. `main.py` 실행
2. `Settings` 로드 (config/settings.py)
3. 로깅 설정 (setup_logging)
4. `RedArrowSystem` 초기화
   - `TechnicalIndicators` 생성
   - `StockSelector` 생성
   - `RiskManager` 생성
5. 메인 루프 실행
   - 시장 데이터 수집
   - 종목 선정
   - 매매 실행
   - 포지션 모니터링

---

## 12. 향후 추가 예정 프로그램

| 우선순위 | 프로그램명 | 설명 |
|---------|-----------|------|
| HIGH | notification.py | 알림 시스템 (슬랙, 텔레그램, 이메일) |
| HIGH | database.py | 데이터베이스 연동 (PostgreSQL, Redis) |
| MEDIUM | backtester.py | 백테스팅 시스템 |
| MEDIUM | reporter.py | 성과 리포트 생성 |
| LOW | web_interface.py | 웹 대시보드 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 초기 프로그램 목록 작성 | RedArrow Team |

---

**문서 끝**
