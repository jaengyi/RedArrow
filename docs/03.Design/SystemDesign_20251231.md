# RedArrow - 시스템 설계서

## 문서 정보
- **작성일**: 2025-12-31
- **최종 수정일**: 2025-12-31
- **버전**: 1.0
- **작성자**: RedArrow Team

---

## 1. 개요

### 1.1 문서 목적
본 문서는 RedArrow 단기투자 종목 선정 시스템의 전체 아키텍처와 각 모듈의 설계를 기술합니다.

### 1.2 시스템 개요
- **시스템 명**: RedArrow Trading System
- **시스템 유형**: 자동 종목 선정 및 트레이딩 시스템
- **주요 기능**: 기술적 지표 기반 단기투자 종목 선정 및 리스크 관리

---

## 2. 시스템 아키텍처

### 2.1 전체 구조도

```
┌─────────────────────────────────────────────────────────────┐
│                  RedArrow Trading System                     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Configuration │    │  Data Layer  │    │ Core Engine  │
│   Module     │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        │           ┌───────┴────────┐         │
        │           │                │         │
        │           ▼                ▼         │
        │    ┌──────────┐    ┌──────────┐     │
        │    │PostgreSQL│    │  Redis   │     │
        │    └──────────┘    └──────────┘     │
        │                                      │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Indicators  │  │Stock Selector│  │Risk Manager  │
│    Module    │  │    Module    │  │   Module     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Broker API   │
                    │  Integration │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ 증권사 API   │
                    │ (외부 시스템)│
                    └──────────────┘
```

### 2.2 계층 구조

#### 2.2.1 Presentation Layer (프레젠테이션 계층)
- **역할**: 사용자 인터페이스 및 로깅
- **구성요소**:
  - 메인 실행 파일 (main.py)
  - 로그 시스템
  - 알림 시스템

#### 2.2.2 Business Logic Layer (비즈니스 로직 계층)
- **역할**: 핵심 비즈니스 로직 처리
- **구성요소**:
  - 기술적 지표 계산 모듈
  - 종목 선정 엔진
  - 리스크 관리 시스템

#### 2.2.3 Data Access Layer (데이터 접근 계층)
- **역할**: 외부 데이터 소스와의 통신
- **구성요소**:
  - 증권사 API 연동
  - 데이터베이스 연동
  - 캐시 시스템

#### 2.2.4 Infrastructure Layer (인프라 계층)
- **역할**: 시스템 인프라 및 설정
- **구성요소**:
  - 설정 관리
  - 환경 변수 관리
  - 스케줄러

---

## 3. 모듈 설계

### 3.1 Configuration Module (설정 관리 모듈)

#### 3.1.1 설계 목적
- 시스템 설정의 중앙 집중 관리
- 환경별 설정 분리
- 설정 검증 및 안전성 보장

#### 3.1.2 주요 클래스

**Settings 클래스**
```python
class Settings:
    """설정 관리 클래스"""

    # 속성 (Properties)
    - broker_type: str           # 증권사 타입
    - trading_mode: str          # 거래 모드
    - db_config: Dict           # 데이터베이스 설정
    - redis_config: Dict        # Redis 설정
    - stock_selector_config: Dict
    - indicators_config: Dict
    - risk_management_config: Dict

    # 메서드 (Methods)
    + __init__(config_path: str)
    + validate() -> bool
    + print_summary() -> None
```

#### 3.1.3 설정 파일 구조
- `config/config.yaml`: 프로그램 설정
- `.env`: 환경 변수 (API 키, DB 정보 등)

---

### 3.2 Technical Indicators Module (기술적 지표 모듈)

#### 3.2.1 설계 목적
- 다양한 기술적 지표 계산 제공
- 재사용 가능한 지표 함수 라이브러리
- 성능 최적화된 계산

#### 3.2.2 주요 클래스

**TechnicalIndicators 클래스**
```python
class TechnicalIndicators:
    """기술적 지표 계산 클래스"""

    # 이동평균
    + calculate_ma(data: Series, period: int) -> Series
    + calculate_ema(data: Series, period: int) -> Series

    # 추세 지표
    + calculate_macd(data: Series, ...) -> Dict[str, Series]
    + calculate_bollinger_bands(data: Series, ...) -> Dict

    # 모멘텀 지표
    + calculate_stochastic(high, low, close, ...) -> Dict
    + calculate_rsi(data: Series, period: int) -> Series

    # 거래량 지표
    + calculate_obv(close: Series, volume: Series) -> Series

    # 변동성 지표
    + calculate_volatility_breakout(open, prev_high, prev_low, k) -> float

    # 패턴 감지
    + detect_golden_cross(short_ma, long_ma) -> Series
    + detect_dead_cross(short_ma, long_ma) -> Series
```

#### 3.2.3 지표 계산 알고리즘

**이동평균선 (MA)**
```
MA(n) = (P1 + P2 + ... + Pn) / n
```

**MACD**
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(MACD Line, 9)
Histogram = MACD Line - Signal Line
```

**스토캐스틱**
```
%K = 100 × (현재가 - 최저가) / (최고가 - 최저가)
%D = %K의 이동평균
```

**OBV**
```
if 종가 > 전일종가: OBV = 전일OBV + 거래량
if 종가 < 전일종가: OBV = 전일OBV - 거래량
if 종가 = 전일종가: OBV = 전일OBV
```

**변동성 돌파**
```
매수기준가 = 당일시가 + (전일고가 - 전일저가) × K
K = 0.5 (기본값)
```

---

### 3.3 Stock Selector Module (종목 선정 모듈)

#### 3.3.1 설계 목적
- PDF 로직 기반 종목 선정 자동화
- 다중 지표 기반 점수 시스템
- 실시간 종목 스크리닝

#### 3.3.2 주요 클래스

**StockSelector 클래스**
```python
class StockSelector:
    """종목 선정 클래스"""

    # 속성
    - config: Dict
    - indicators: TechnicalIndicators
    - top_volume_count: int
    - volume_surge_threshold: float
    - k_value: float

    # 필터링 메서드
    + filter_by_volume_amount(stock_data, top_n) -> DataFrame

    # 감지 메서드
    + detect_volume_surge(current_volume, avg_volume) -> bool
    + check_ma_breakout(price_data, current_price) -> bool
    + check_golden_cross(price_data) -> bool
    + check_volatility_breakout(open, prev_high, prev_low, current) -> bool

    # 신호 분석
    + check_macd_signal(price_data) -> Dict
    + check_stochastic_signal(high, low, close) -> Dict
    + check_obv_trend(close, volume) -> bool

    # 패턴 감지
    + detect_order_book_imbalance(bid_volume, ask_volume) -> Dict
    + detect_support_at_ma(price_data, current_price) -> bool

    # 메인 로직
    + select_stocks(stock_data, price_history) -> List[Dict]
```

#### 3.3.3 종목 선정 알고리즘

**선정 프로세스**
```
1. 거래대금 상위 30개 종목 필터링
2. 각 종목에 대해 다음 신호 평가:
   - 거래량 폭증 (3점)
   - 골든크로스 (3점)
   - 이동평균선 돌파 (2점)
   - 변동성 돌파 (2점)
   - MACD 매수 신호 (2점)
   - 스토캐스틱 매수 신호 (2점)
   - OBV 상승 (1점)
   - 눌림목 형성 (1점)
3. 총점 5점 이상인 종목 선정
4. 점수 순으로 정렬하여 반환
```

**점수 계산 로직**
```python
score = 0
if volume_surge: score += 3
if golden_cross: score += 3
if ma_breakout: score += 2
if volatility_breakout: score += 2
if macd_buy: score += 2
if stochastic_buy: score += 2
if obv_rising: score += 1
if support_at_ma: score += 1

if score >= 5:
    선정 종목에 추가
```

---

### 3.4 Risk Manager Module (리스크 관리 모듈)

#### 3.4.1 설계 목적
- 손실 최소화 및 수익 보호
- 자동화된 손익 관리
- 포트폴리오 리스크 제어

#### 3.4.2 주요 클래스

**RiskManager 클래스**
```python
class RiskManager:
    """리스크 관리 클래스"""

    # 속성
    - stop_loss_percent: float
    - take_profit_percent: float
    - trailing_stop: bool
    - max_position_size: int
    - max_positions: int
    - overnight_hold: bool
    - daily_loss_limit: float

    # 손익 관리
    + check_stop_loss(entry_price, current_price, ma_value) -> Dict
    + check_take_profit(entry_price, current_price) -> Dict
    + calculate_trailing_stop(entry_price, highest_price, current_price) -> Dict

    # 포지션 관리
    + calculate_position_size(stock_price, account_balance, risk_percent) -> Dict
    + check_max_positions(current_positions) -> bool

    # 전략 관리
    + check_overnight_eligibility(entry_price, current_price, market_status) -> Dict
    + check_daily_loss_limit(daily_pnl, account_balance) -> Dict

    # 종합 판단
    + should_close_position(entry_price, current_price, highest_price, ...) -> Dict
```

#### 3.4.3 리스크 관리 알고리즘

**손절 로직**
```
조건 1: (현재가 - 매수가) / 매수가 × 100 <= -2.5%
조건 2: 현재가 < 이동평균선

if 조건1 OR 조건2:
    손절 실행
```

**익절 로직**
```
수익률 = (현재가 - 매수가) / 매수가 × 100

if 수익률 >= 5.0%:
    익절 실행
```

**트레일링 스톱**
```
최고가 대비 하락률 = (현재가 - 최고가) / 최고가 × 100
트레일링 스톱 가격 = 최고가 × (1 - 1.5%)

if 하락률 <= -1.5% AND 현재가 > 매수가:
    트레일링 스톱 실행
```

**포지션 크기 계산**
```
리스크 금액 = 계좌 잔고 × 2%
매수 수량 = 리스크 금액 / (주가 × 손절률)
최종 수량 = min(매수 수량, 최대포지션크기/주가)
```

**오버나이트 판단**
```
if 오버나이트 설정 OFF:
    return 청산

수익률 = (현재가 - 매수가) / 매수가 × 100

if 수익률 < 2.0%:
    return 청산

if 시장상태 == '불안정':
    return 청산

return 보유
```

---

### 3.5 Broker API Module (증권사 API 모듈)

#### 3.5.1 설계 목적
- 증권사 API와의 표준화된 인터페이스
- 다중 증권사 지원
- 오류 처리 및 재연결 로직

#### 3.5.2 주요 인터페이스

**BrokerAPI 추상 클래스**
```python
class BrokerAPI(ABC):
    """증권사 API 추상 클래스"""

    # 연결 관리
    + connect() -> bool
    + disconnect() -> None

    # 데이터 조회
    + get_top_volume_stocks(count: int) -> DataFrame
    + get_stock_price(stock_code: str) -> Dict
    + get_historical_data(stock_code: str, days: int) -> DataFrame
    + get_minute_data(stock_code: str, interval: int) -> DataFrame
    + get_order_book(stock_code: str) -> Dict

    # 주문 실행
    + place_buy_order(stock_code, quantity, price) -> Dict
    + place_sell_order(stock_code, quantity, price) -> Dict

    # 계좌 관리
    + get_account_balance() -> Dict
    + get_positions() -> List[Dict]
```

#### 3.5.3 API 연동 시퀀스

**매수 주문 시퀀스**
```
1. 종목 선정
2. 포지션 크기 계산
3. API 연결 확인
4. 계좌 잔고 조회
5. 매수 주문 전송
6. 주문 체결 확인
7. 포지션 기록
8. 로그 저장
```

---

## 4. 데이터 모델

### 4.1 종목 데이터 구조

```python
# 현재 종목 데이터
StockData = {
    'code': str,           # 종목 코드
    'name': str,           # 종목명
    'price': float,        # 현재가
    'open': float,         # 시가
    'high': float,         # 고가
    'low': float,          # 저가
    'close': float,        # 종가
    'volume': int,         # 거래량
    'amount': int,         # 거래대금
    'change_rate': float,  # 등락률
    'prev_high': float,    # 전일 고가
    'prev_low': float      # 전일 저가
}

# 과거 가격 데이터
PriceHistory = DataFrame(
    columns=['open', 'high', 'low', 'close', 'volume'],
    index=DatetimeIndex
)

# 선정 종목 데이터
SelectedStock = {
    'code': str,
    'name': str,
    'price': float,
    'volume': int,
    'amount': int,
    'change_rate': float,
    'score': int,          # 선정 점수
    'signals': Dict,       # 발생 신호들
    'timestamp': datetime  # 선정 시각
}
```

### 4.2 포지션 데이터 구조

```python
Position = {
    'name': str,           # 종목명
    'entry_price': float,  # 진입가
    'quantity': int,       # 보유 수량
    'highest_price': float,# 최고가
    'entry_time': datetime,# 진입 시각
    'stop_loss_price': float,    # 손절가 (선택)
    'take_profit_price': float   # 익절가 (선택)
}
```

---

## 5. 인터페이스 설계

### 5.1 모듈 간 인터페이스

#### 5.1.1 StockSelector ↔ TechnicalIndicators
```python
# StockSelector가 TechnicalIndicators 사용
indicators = TechnicalIndicators()
ma_20 = indicators.calculate_ma(price_data, 20)
macd = indicators.calculate_macd(price_data)
```

#### 5.1.2 Main ↔ StockSelector
```python
# Main이 StockSelector 사용
selector = StockSelector(config)
selected_stocks = selector.select_stocks(stock_data, price_history)
```

#### 5.1.3 Main ↔ RiskManager
```python
# Main이 RiskManager 사용
risk_manager = RiskManager(config)
should_close = risk_manager.should_close_position(
    entry_price, current_price, highest_price
)
```

### 5.2 외부 시스템 인터페이스

#### 5.2.1 증권사 API
- **프로토콜**: REST API / WebSocket
- **인증**: OAuth2 / API Key
- **데이터 형식**: JSON

#### 5.2.2 데이터베이스
- **PostgreSQL**:
  - 연결: psycopg2
  - 포트: 5432
  - 데이터 형식: SQL

- **Redis**:
  - 연결: redis-py
  - 포트: 6379
  - 데이터 형식: Key-Value

---

## 6. 처리 흐름

### 6.1 메인 실행 흐름

```
[시작]
  │
  ├─ 설정 로드
  │   ├─ config.yaml 읽기
  │   └─ .env 환경변수 로드
  │
  ├─ 설정 검증
  │   ├─ API 키 확인
  │   └─ DB 연결 확인
  │
  ├─ 모듈 초기화
  │   ├─ StockSelector 생성
  │   ├─ RiskManager 생성
  │   └─ TechnicalIndicators 생성
  │
  ├─ [메인 루프 시작]
  │   │
  │   ├─ 시장 개장 확인
  │   │   └─ 개장 시간이 아니면 대기
  │   │
  │   ├─ 일일 손실 제한 확인
  │   │   └─ 제한 도달 시 종료
  │   │
  │   ├─ 시장 데이터 수집
  │   │   ├─ 거래대금 상위 종목 조회
  │   │   └─ 과거 가격 데이터 조회
  │   │
  │   ├─ 종목 선정
  │   │   ├─ 각 종목에 대해 지표 계산
  │   │   ├─ 신호 평가
  │   │   └─ 점수 기반 선정
  │   │
  │   ├─ 매매 실행 (시뮬레이션)
  │   │   ├─ 포지션 수 확인
  │   │   ├─ 포지션 크기 계산
  │   │   └─ 매수 주문 (시뮬레이션)
  │   │
  │   ├─ 포지션 모니터링
  │   │   ├─ 각 포지션에 대해
  │   │   ├─ 현재가 조회
  │   │   ├─ 청산 여부 판단
  │   │   └─ 필요 시 매도 주문
  │   │
  │   └─ 결과 로깅
  │
  └─ [종료]
```

### 6.2 종목 선정 상세 흐름

```
[종목 선정 시작]
  │
  ├─ 거래대금 상위 30개 필터링
  │
  ├─ [각 종목에 대해]
  │   │
  │   ├─ 과거 데이터 확인
  │   │   └─ 없으면 스킵
  │   │
  │   ├─ 점수 초기화 (score = 0)
  │   │
  │   ├─ [신호 평가]
  │   │   │
  │   │   ├─ 거래량 폭증 확인
  │   │   │   └─ True면 score += 3
  │   │   │
  │   │   ├─ 이동평균선 돌파 확인
  │   │   │   └─ True면 score += 2
  │   │   │
  │   │   ├─ 골든크로스 확인
  │   │   │   └─ True면 score += 3
  │   │   │
  │   │   ├─ 변동성 돌파 확인
  │   │   │   └─ True면 score += 2
  │   │   │
  │   │   ├─ MACD 신호 확인
  │   │   │   └─ 매수 신호면 score += 2
  │   │   │
  │   │   ├─ 스토캐스틱 신호 확인
  │   │   │   └─ 매수 신호면 score += 2
  │   │   │
  │   │   ├─ OBV 상승 확인
  │   │   │   └─ True면 score += 1
  │   │   │
  │   │   └─ 눌림목 형성 확인
  │   │       └─ True면 score += 1
  │   │
  │   └─ if score >= 5:
  │       └─ 선정 목록에 추가
  │
  ├─ 점수 순으로 정렬
  │
  └─ [종목 선정 완료]
```

---

## 7. 오류 처리

### 7.1 오류 유형 및 처리 방법

| 오류 유형 | 처리 방법 |
|----------|----------|
| API 연결 실패 | 재연결 시도 (최대 3회), 실패 시 로그 기록 후 대기 |
| 데이터 조회 실패 | 해당 종목 스킵, 다음 종목 처리 |
| 주문 실패 | 로그 기록, 알림 발송, 재시도 안함 |
| 설정 검증 실패 | 프로그램 즉시 종료, 오류 메시지 출력 |
| 데이터베이스 연결 실패 | 재연결 시도, 실패 시 임시 메모리 사용 |

### 7.2 로깅 정책

**로그 레벨**
- DEBUG: 상세 디버깅 정보
- INFO: 일반 정보 (종목 선정, 주문 실행 등)
- WARNING: 경고 (재연결, 데이터 누락 등)
- ERROR: 오류 (API 실패, 주문 실패 등)
- CRITICAL: 치명적 오류 (설정 오류, 시스템 중단 등)

**로그 파일**
- 파일명: `redarrow_YYYYMMDD.log`
- 위치: `logs/` 디렉토리
- 보관 기간: 30일

---

## 8. 성능 요구사항

### 8.1 응답 시간
- 종목 선정: 30초 이내 (30개 종목 기준)
- 지표 계산: 1초 이내 (단일 종목, 30일 데이터)
- 주문 실행: 3초 이내

### 8.2 처리량
- 동시 모니터링 종목: 최대 30개
- 동시 보유 포지션: 최대 5개
- 데이터 수집 주기: 1초

### 8.3 리소스 사용
- CPU: 최대 50% (4코어 기준)
- 메모리: 최대 2GB
- 디스크: 로그 및 데이터베이스 포함 10GB

---

## 9. 보안 설계

### 9.1 인증 및 권한
- API 키 암호화 저장 (환경 변수)
- 데이터베이스 접근 권한 제한
- 민감 정보 로그 마스킹

### 9.2 통신 보안
- HTTPS 통신 강제
- API 요청 시 인증 토큰 포함
- 타임아웃 설정 (30초)

### 9.3 데이터 보안
- API 키 Git 제외 (.gitignore)
- 거래 로그 암호화 저장
- 개인정보 비식별 처리

---

## 10. 확장성 설계

### 10.1 모듈 확장
- 새로운 지표 추가: TechnicalIndicators 클래스에 메서드 추가
- 새로운 선정 로직: StockSelector 점수 계산 로직 수정
- 새로운 증권사 지원: BrokerAPI 구현 클래스 추가

### 10.2 데이터 확장
- 분산 데이터베이스 지원 (Sharding)
- 캐시 레이어 추가 (Redis)
- 실시간 스트리밍 (WebSocket)

### 10.3 배포 확장
- Docker 컨테이너화
- Kubernetes 오케스트레이션
- 클라우드 배포 (AWS, GCP, Azure)

---

## 부록

### A. 용어 정의

| 용어 | 정의 |
|------|------|
| 단타 | 당일 매수 후 당일 매도하는 초단기 투자 |
| 스캘핑 | 분 단위의 극단적 단기 매매 |
| 골든크로스 | 단기 이동평균선이 장기 이동평균선을 상향 돌파 |
| 데드크로스 | 단기 이동평균선이 장기 이동평균선을 하향 돌파 |
| 눌림목 | 상승 추세 중 일시적 조정 후 재상승 패턴 |
| VI | Volatility Interruption, 변동성 완화 장치 |

### B. 참고 문서
- `docs/01.Requirement/Requirements_20251231.md`
- `docs/02.Analysis/TechnicalAnalysis_20251231.md`
- `docs/02.Analysis/NotebookLM_20251231.pdf`

### C. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 초기 설계서 작성 | RedArrow Team |

---

**문서 끝**
