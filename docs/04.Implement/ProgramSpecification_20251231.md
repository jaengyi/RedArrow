# RedArrow - 프로그램 사양서

## 문서 정보
- **작성일**: 2025-12-31
- **최종 수정일**: 2025-12-31
- **버전**: 1.0
- **작성자**: RedArrow Team

---

## 1. 개요

본 문서는 RedArrow 시스템의 핵심 프로그램들에 대한 상세 사양을 기술합니다.

---

## 2. 메인 프로그램 사양

### 2.1 main.py

#### 2.1.1 프로그램 개요
- **파일명**: `src/main.py`
- **목적**: 시스템 전체 실행 및 제어
- **주요 기능**: 모듈 초기화, 메인 루프 실행, 종목 선정 및 매매 제어

#### 2.1.2 함수 사양

**setup_logging(config: Dict) -> logging.Logger**
```python
def setup_logging(config: Dict) -> logging.Logger
```
- **기능**: 로깅 시스템 초기화
- **입력**:
  - config (Dict): 로깅 설정 딕셔너리
    - level (str): 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR")
    - log_dir (str): 로그 디렉토리 경로
- **출력**: logging.Logger 객체
- **처리 로직**:
  1. 로그 디렉토리 생성
  2. 로그 파일명 생성 (redarrow_YYYYMMDD.log)
  3. 로그 핸들러 설정 (파일, 콘솔)
  4. 로거 반환

**main()**
```python
def main() -> None
```
- **기능**: 메인 진입점
- **입력**: 없음
- **출력**: 없음
- **처리 로직**:
  1. 시작 메시지 출력
  2. RedArrowSystem 인스턴스 생성
  3. system.run() 호출

#### 2.1.3 클래스 사양

**RedArrowSystem**
```python
class RedArrowSystem:
    def __init__(self)
    def is_market_open(self) -> bool
    def collect_market_data(self) -> Dict
    def select_stocks(self, market_data: Dict) -> List[Dict]
    def execute_trade(self, stock: Dict) -> None
    def monitor_positions(self) -> None
    def check_daily_limit(self) -> bool
    def run(self) -> None
```

**속성**:
- settings (Settings): 설정 객체
- logger (logging.Logger): 로거 객체
- stock_selector (StockSelector): 종목 선정 객체
- risk_manager (RiskManager): 리스크 관리 객체
- indicators (TechnicalIndicators): 지표 계산 객체
- positions (Dict): 보유 포지션 딕셔너리
- daily_pnl (float): 당일 손익
- account_balance (float): 계좌 잔고

**메서드 상세**:

**__init__()**
- **기능**: 시스템 초기화
- **처리 로직**:
  1. 설정 로드 (Settings)
  2. 로깅 설정
  3. 설정 검증
  4. 모듈 초기화 (StockSelector, RiskManager, TechnicalIndicators)
  5. 상태 변수 초기화

**is_market_open() -> bool**
- **기능**: 시장 개장 시간 확인
- **출력**: 개장 여부 (bool)
- **처리 로직**:
  1. 현재 시간 조회
  2. market_hours 설정과 비교
  3. 개장 시간 내이면 True 반환

**collect_market_data() -> Dict**
- **기능**: 시장 데이터 수집
- **출력**: 시장 데이터 딕셔너리
  - stock_data (DataFrame): 종목 데이터
  - price_history (Dict[str, DataFrame]): 과거 가격 데이터
- **처리 로직**:
  1. 증권사 API를 통해 데이터 수집
  2. 데이터 정규화
  3. 딕셔너리 형태로 반환
- **참고**: 현재는 예시 데이터 반환, 실제 API 연동 필요

**select_stocks(market_data: Dict) -> List[Dict]**
- **기능**: 종목 선정
- **입력**: market_data (Dict)
- **출력**: 선정된 종목 리스트
- **처리 로직**:
  1. stock_selector.select_stocks() 호출
  2. 선정 결과 로깅
  3. 종목 리스트 반환

**execute_trade(stock: Dict)**
- **기능**: 매매 실행
- **입력**: stock (Dict) - 선정된 종목 정보
- **처리 로직**:
  1. 포지션 수 확인
  2. 포지션 크기 계산
  3. 매수 주문 실행 (또는 시뮬레이션)
  4. 포지션 기록

**monitor_positions()**
- **기능**: 보유 포지션 모니터링
- **처리 로직**:
  1. 각 포지션에 대해
  2. 현재가 조회
  3. 최고가 업데이트
  4. 청산 여부 판단 (risk_manager.should_close_position)
  5. 필요 시 매도 주문
  6. 손익 기록

**check_daily_limit() -> bool**
- **기능**: 일일 손실 제한 확인
- **출력**: 거래 계속 가능 여부 (bool)
- **처리 로직**:
  1. risk_manager.check_daily_loss_limit() 호출
  2. 제한 도달 시 False 반환

**run()**
- **기능**: 메인 실행 루프
- **처리 로직**:
  1. 시장 개장 확인
  2. 일일 손실 제한 확인
  3. 시장 데이터 수집
  4. 종목 선정
  5. 매매 실행
  6. 포지션 모니터링
  7. 결과 로깅

---

## 3. 설정 관리 모듈 사양

### 3.1 settings.py

#### 3.1.1 프로그램 개요
- **파일명**: `src/config/settings.py`
- **목적**: 시스템 설정 중앙 관리
- **주요 기능**: 환경 변수 로드, YAML 파일 파싱, 설정 검증

#### 3.1.2 클래스 사양

**Settings**
```python
class Settings:
    def __init__(self, config_path: str = None)
    def validate(self) -> bool
    def print_summary(self) -> None
    # Properties
    @property broker_type(self) -> str
    @property trading_mode(self) -> str
    @property db_config(self) -> Dict[str, str]
    @property redis_config(self) -> Dict[str, Any]
    @property stock_selector_config(self) -> Dict[str, Any]
    @property indicators_config(self) -> Dict[str, Any]
    @property risk_management_config(self) -> Dict[str, Any]
    # ... 기타 프로퍼티
```

**속성**:
- root_dir (Path): 프로젝트 루트 디렉토리
- config (Dict): YAML 설정 딕셔너리

**메서드 상세**:

**__init__(config_path: str = None)**
- **기능**: 설정 초기화
- **입력**: config_path (str, optional) - 설정 파일 경로
- **처리 로직**:
  1. 프로젝트 루트 디렉토리 설정
  2. .env 파일 로드 (dotenv)
  3. config.yaml 파일 로드
  4. YAML 파싱

**validate() -> bool**
- **기능**: 필수 설정 검증
- **출력**: 검증 성공 여부 (bool)
- **처리 로직**:
  1. API 키 확인 (APP_KEY, APP_SECRET, ACCOUNT_NUMBER)
  2. 데이터베이스 설정 확인 (DB_USER, DB_PASSWORD)
  3. 오류 목록 수집
  4. 오류 있으면 출력 후 False 반환

**print_summary()**
- **기능**: 설정 요약 출력
- **처리 로직**:
  1. 증권사, 거래 모드 등 주요 설정 출력
  2. 리스크 관리 설정 출력

**프로퍼티 상세**:

각 프로퍼티는 해당 설정값을 반환하며, 환경 변수가 설정되어 있으면 우선적으로 사용합니다.

---

## 4. 기술적 지표 모듈 사양

### 4.1 technical_indicators.py

#### 4.1.1 프로그램 개요
- **파일명**: `src/indicators/technical_indicators.py`
- **목적**: 기술적 지표 계산 제공
- **주요 기능**: 이동평균, MACD, 스토캐스틱, OBV 등 계산

#### 4.1.2 클래스 사양

**TechnicalIndicators**
```python
class TechnicalIndicators:
    def calculate_ma(self, data: pd.Series, period: int) -> pd.Series
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series
    def calculate_macd(self, data: pd.Series, fast_period: int = 12,
                      slow_period: int = 26, signal_period: int = 9) -> Dict
    def calculate_stochastic(self, high: pd.Series, low: pd.Series,
                            close: pd.Series, k_period: int = 14,
                            d_period: int = 3) -> Dict
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series
    def calculate_volatility_breakout(self, open_price: float,
                                     prev_high: float, prev_low: float,
                                     k_value: float = 0.5) -> float
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series
    def detect_golden_cross(self, short_ma: pd.Series,
                           long_ma: pd.Series) -> pd.Series
    def detect_dead_cross(self, short_ma: pd.Series,
                         long_ma: pd.Series) -> pd.Series
    def check_price_above_ma(self, price: float,
                            ma_values: pd.Series) -> bool
    def calculate_bollinger_bands(self, data: pd.Series,
                                 period: int = 20,
                                 num_std: float = 2.0) -> Dict
```

**메서드 상세**:

**calculate_ma(data: pd.Series, period: int) -> pd.Series**
- **기능**: 단순 이동평균 계산
- **입력**:
  - data (pd.Series): 가격 데이터
  - period (int): 이동평균 기간
- **출력**: pd.Series - 이동평균 값
- **수식**: `MA(n) = (P1 + P2 + ... + Pn) / n`
- **처리 로직**:
  1. data.rolling(window=period).mean() 호출
  2. 결과 반환

**calculate_macd(data, fast_period, slow_period, signal_period) -> Dict**
- **기능**: MACD 지표 계산
- **입력**:
  - data (pd.Series): 가격 데이터
  - fast_period (int): 빠른 EMA 기간 (기본 12)
  - slow_period (int): 느린 EMA 기간 (기본 26)
  - signal_period (int): 시그널 라인 기간 (기본 9)
- **출력**: Dict
  - macd (pd.Series): MACD 라인
  - signal (pd.Series): 시그널 라인
  - histogram (pd.Series): 히스토그램
- **수식**:
  - `MACD Line = EMA(12) - EMA(26)`
  - `Signal Line = EMA(MACD Line, 9)`
  - `Histogram = MACD Line - Signal Line`
- **처리 로직**:
  1. 빠른 EMA 계산
  2. 느린 EMA 계산
  3. MACD 라인 = 빠른 EMA - 느린 EMA
  4. 시그널 라인 = MACD 라인의 EMA
  5. 히스토그램 = MACD 라인 - 시그널 라인
  6. 딕셔너리로 반환

**calculate_stochastic(high, low, close, k_period, d_period) -> Dict**
- **기능**: 스토캐스틱 지표 계산
- **입력**:
  - high (pd.Series): 고가 데이터
  - low (pd.Series): 저가 데이터
  - close (pd.Series): 종가 데이터
  - k_period (int): %K 기간 (기본 14)
  - d_period (int): %D 기간 (기본 3)
- **출력**: Dict
  - %K (pd.Series): %K 라인
  - %D (pd.Series): %D 라인
- **수식**:
  - `%K = 100 × (현재가 - 최저가) / (최고가 - 최저가)`
  - `%D = %K의 이동평균`
- **처리 로직**:
  1. k_period 기간 동안 최저가, 최고가 계산
  2. %K 계산
  3. %D = %K의 이동평균 계산
  4. 딕셔너리로 반환

**calculate_obv(close, volume) -> pd.Series**
- **기능**: OBV (On-Balance Volume) 계산
- **입력**:
  - close (pd.Series): 종가 데이터
  - volume (pd.Series): 거래량 데이터
- **출력**: pd.Series - OBV 값
- **수식**:
  - `if 종가 > 전일종가: OBV = 전일OBV + 거래량`
  - `if 종가 < 전일종가: OBV = 전일OBV - 거래량`
  - `if 종가 = 전일종가: OBV = 전일OBV`
- **처리 로직**:
  1. OBV Series 초기화
  2. 첫 값 = 첫 거래량
  3. 나머지 값들을 순회하며:
     - 종가 비교
     - OBV 누적 계산
  4. 결과 반환

**calculate_volatility_breakout(open_price, prev_high, prev_low, k_value) -> float**
- **기능**: 변동성 돌파 기준가 계산
- **입력**:
  - open_price (float): 당일 시가
  - prev_high (float): 전일 고가
  - prev_low (float): 전일 저가
  - k_value (float): K값 (기본 0.5)
- **출력**: float - 돌파 기준가
- **수식**: `매수기준가 = 당일시가 + (전일고가 - 전일저가) × K`
- **처리 로직**:
  1. 전일 변동폭 = 전일고가 - 전일저가
  2. 돌파가 = 당일시가 + (전일변동폭 × K)
  3. 결과 반환

**detect_golden_cross(short_ma, long_ma) -> pd.Series**
- **기능**: 골든크로스 감지
- **입력**:
  - short_ma (pd.Series): 단기 이동평균
  - long_ma (pd.Series): 장기 이동평균
- **출력**: pd.Series - 골든크로스 발생 여부 (True/False)
- **처리 로직**:
  1. 이전 시점: short_ma <= long_ma
  2. 현재 시점: short_ma > long_ma
  3. 두 조건 모두 만족하면 True
  4. 결과 반환

---

## 5. 종목 선정 모듈 사양

### 5.1 selector.py

#### 5.1.1 프로그램 개요
- **파일명**: `src/stock_selector/selector.py`
- **목적**: 기술적 지표 기반 종목 선정
- **주요 기능**: 다중 지표 평가, 점수 계산, 종목 필터링

#### 5.1.2 클래스 사양

**StockSelector**
```python
class StockSelector:
    def __init__(self, config: Dict)
    def filter_by_volume_amount(self, stock_data: pd.DataFrame,
                                top_n: Optional[int] = None) -> pd.DataFrame
    def detect_volume_surge(self, current_volume: float,
                           avg_volume: float,
                           threshold: Optional[float] = None) -> bool
    def check_ma_breakout(self, price_data: pd.Series,
                         current_price: float,
                         ma_period: int = 20) -> bool
    def check_golden_cross(self, price_data: pd.Series,
                          short_period: int = 5,
                          long_period: int = 20) -> bool
    def check_volatility_breakout(self, open_price: float,
                                  prev_high: float, prev_low: float,
                                  current_price: float) -> bool
    def check_macd_signal(self, price_data: pd.Series) -> Dict
    def check_stochastic_signal(self, high_data: pd.Series,
                               low_data: pd.Series,
                               close_data: pd.Series) -> Dict
    def check_obv_trend(self, close_data: pd.Series,
                       volume_data: pd.Series) -> bool
    def detect_order_book_imbalance(self, bid_volume: float,
                                    ask_volume: float) -> Dict
    def detect_support_at_ma(self, price_data: pd.Series,
                            current_price: float,
                            ma_period: int = 20,
                            tolerance: float = 0.01) -> bool
    def select_stocks(self, stock_data: pd.DataFrame,
                     price_history: Dict[str, pd.DataFrame]) -> List[Dict]
```

**속성**:
- config (Dict): 설정 딕셔너리
- indicators (TechnicalIndicators): 지표 계산 객체
- top_volume_count (int): 거래대금 상위 종목 수
- volume_surge_threshold (float): 거래량 폭증 기준
- k_value (float): 변동성 돌파 K값
- ma_periods (Dict): 이동평균 기간 설정
- macd_config (Dict): MACD 설정
- stochastic_config (Dict): 스토캐스틱 설정

**메서드 상세**:

**select_stocks(stock_data, price_history) -> List[Dict]**
- **기능**: 종목 선정 메인 로직
- **입력**:
  - stock_data (pd.DataFrame): 현재 종목 데이터
    - 필수 컬럼: code, name, price, volume, amount, change_rate, open, high, low, close, prev_high, prev_low
  - price_history (Dict[str, pd.DataFrame]): 종목별 과거 가격 데이터
    - key: 종목 코드
    - value: DataFrame (컬럼: open, high, low, close, volume)
- **출력**: List[Dict] - 선정된 종목 리스트
  - 각 종목: {code, name, price, volume, amount, change_rate, score, signals, timestamp}
- **처리 로직**:
  1. 거래대금 상위 종목 필터링 (top_volume_count개)
  2. 각 종목에 대해:
     - 과거 데이터 확인 (없으면 스킵)
     - 점수 초기화 (score = 0)
     - 거래량 폭증 확인 (+3점)
     - 이동평균선 돌파 확인 (+2점)
     - 골든크로스 확인 (+3점)
     - 변동성 돌파 확인 (+2점)
     - MACD 매수 신호 확인 (+2점)
     - 스토캐스틱 매수 신호 확인 (+2점)
     - OBV 상승 확인 (+1점)
     - 눌림목 형성 확인 (+1점)
     - if score >= 5: 선정 목록에 추가
  3. 점수 순으로 정렬
  4. 결과 반환

**check_macd_signal(price_data) -> Dict**
- **기능**: MACD 매수/매도 신호 확인
- **입력**: price_data (pd.Series)
- **출력**: Dict - {buy: bool, sell: bool}
- **처리 로직**:
  1. MACD 계산 (indicators.calculate_macd)
  2. 매수 신호: MACD가 시그널선을 상향 돌파
  3. 매도 신호: MACD가 시그널선을 하향 돌파
  4. 결과 반환

---

## 6. 리스크 관리 모듈 사양

### 6.1 risk_control.py

#### 6.1.1 프로그램 개요
- **파일명**: `src/risk_manager/risk_control.py`
- **목적**: 손익 관리 및 리스크 제어
- **주요 기능**: 손절/익절 판단, 포지션 크기 계산, 오버나이트 관리

#### 6.1.2 클래스 사양

**RiskManager**
```python
class RiskManager:
    def __init__(self, config: Dict)
    def check_stop_loss(self, entry_price: float, current_price: float,
                       ma_value: Optional[float] = None) -> Dict
    def check_take_profit(self, entry_price: float,
                         current_price: float) -> Dict
    def calculate_trailing_stop(self, entry_price: float,
                                highest_price: float,
                                current_price: float) -> Dict
    def calculate_position_size(self, stock_price: float,
                               account_balance: float,
                               risk_percent: float = 2.0) -> Dict
    def check_max_positions(self, current_positions: int) -> bool
    def check_overnight_eligibility(self, entry_price: float,
                                    current_price: float,
                                    market_status: str = 'normal') -> Dict
    def check_daily_loss_limit(self, daily_pnl: float,
                               account_balance: float) -> Dict
    def should_close_position(self, entry_price: float,
                             current_price: float,
                             highest_price: float,
                             ma_value: Optional[float] = None,
                             current_time: Optional[datetime] = None) -> Dict
```

**속성**:
- stop_loss_percent (float): 손절 기준 (%)
- take_profit_percent (float): 익절 기준 (%)
- trailing_stop (bool): 트레일링 스톱 활성화 여부
- trailing_stop_percent (float): 트레일링 스톱 하락률 (%)
- max_position_size (int): 단일 종목 최대 투자금
- max_positions (int): 최대 동시 보유 종목 수
- overnight_hold (bool): 오버나이트 보유 허용
- overnight_min_profit (float): 오버나이트 최소 수익률 (%)
- daily_loss_limit (float): 일일 최대 손실률 (%)

**메서드 상세**:

**check_stop_loss(entry_price, current_price, ma_value) -> Dict**
- **기능**: 손절 기준 확인
- **입력**:
  - entry_price (float): 매수가
  - current_price (float): 현재가
  - ma_value (float, optional): 이동평균선 값
- **출력**: Dict
  - should_stop (bool): 손절 여부
  - reason (str): 손절 사유
  - loss_percent (float): 손실률
- **처리 로직**:
  1. 손실률 = (현재가 - 매수가) / 매수가 × 100
  2. if 손실률 <= -stop_loss_percent: return True (퍼센트 손절)
  3. if ma_value 존재 and 현재가 < ma_value: return True (이평선 손절)
  4. else: return False

**calculate_position_size(stock_price, account_balance, risk_percent) -> Dict**
- **기능**: 포지션 크기 계산
- **입력**:
  - stock_price (float): 주식 가격
  - account_balance (float): 계좌 잔고
  - risk_percent (float): 리스크 비율 (기본 2%)
- **출력**: Dict
  - quantity (int): 매수 수량
  - amount (float): 매수 금액
  - risk_amount (float): 리스크 금액
- **수식**:
  - `리스크 금액 = 계좌잔고 × risk_percent / 100`
  - `매수 수량 = 리스크금액 / (주가 × 손절률 / 100)`
  - `최종 수량 = min(매수수량, max_position_size / 주가)`
- **처리 로직**:
  1. 리스크 금액 계산
  2. 손절가 기준 매수 수량 계산
  3. 최대 포지션 크기 제한 적용
  4. 실제 매수 금액 계산
  5. 결과 반환

**should_close_position(entry_price, current_price, highest_price, ...) -> Dict**
- **기능**: 포지션 청산 여부 종합 판단
- **입력**:
  - entry_price (float): 매수가
  - current_price (float): 현재가
  - highest_price (float): 매수 후 최고가
  - ma_value (float, optional): 이동평균선 값
  - current_time (datetime, optional): 현재 시간
- **출력**: Dict
  - should_close (bool): 청산 여부
  - reason (str): 청산 사유
  - pnl_percent (float): 손익률
- **처리 로직**:
  1. 손절 확인 (check_stop_loss)
  2. 익절 확인 (check_take_profit)
  3. 트레일링 스톱 확인 (calculate_trailing_stop)
  4. 장 마감 시간 확인 (15:20 이후)
     - 오버나이트 적격성 확인 (check_overnight_eligibility)
  5. 청산 조건 만족 시 사유와 함께 True 반환

---

## 7. 증권사 API 모듈 사양

### 7.1 broker_api.py

#### 7.1.1 프로그램 개요
- **파일명**: `src/data_collectors/broker_api.py`
- **목적**: 증권사 API 연동 표준화
- **주요 기능**: 데이터 조회, 주문 실행, 계좌 관리

#### 7.1.2 클래스 사양

**BrokerAPI (추상 클래스)**
```python
from abc import ABC, abstractmethod

class BrokerAPI(ABC):
    def __init__(self, config: Dict)
    @abstractmethod
    def connect(self) -> bool
    @abstractmethod
    def disconnect(self) -> None
    @abstractmethod
    def get_top_volume_stocks(self, count: int = 30) -> pd.DataFrame
    @abstractmethod
    def get_stock_price(self, stock_code: str) -> Dict
    @abstractmethod
    def get_historical_data(self, stock_code: str,
                           days: int = 30) -> pd.DataFrame
    @abstractmethod
    def get_minute_data(self, stock_code: str,
                       interval: int = 1) -> pd.DataFrame
    @abstractmethod
    def get_order_book(self, stock_code: str) -> Dict
    @abstractmethod
    def place_buy_order(self, stock_code: str, quantity: int,
                       price: Optional[float] = None) -> Dict
    @abstractmethod
    def place_sell_order(self, stock_code: str, quantity: int,
                        price: Optional[float] = None) -> Dict
    @abstractmethod
    def get_account_balance(self) -> Dict
    @abstractmethod
    def get_positions(self) -> List[Dict]
```

**속성**:
- config (Dict): API 설정
- is_connected (bool): 연결 상태

**메서드 상세**:

**get_top_volume_stocks(count) -> pd.DataFrame**
- **기능**: 거래대금 상위 종목 조회
- **입력**: count (int) - 조회할 종목 수
- **출력**: pd.DataFrame
  - 컬럼: code, name, price, volume, amount, change_rate, open, high, low, close
- **구현 방법**: 증권사별로 구체 클래스에서 구현

**place_buy_order(stock_code, quantity, price) -> Dict**
- **기능**: 매수 주문
- **입력**:
  - stock_code (str): 종목 코드
  - quantity (int): 주문 수량
  - price (float, optional): 주문 가격 (None이면 시장가)
- **출력**: Dict
  - order_id (str): 주문 번호
  - status (str): 주문 상태 ("submitted", "filled", "rejected")
  - message (str): 메시지
- **구현 방법**: 증권사별로 구체 클래스에서 구현

---

## 8. 데이터 구조 사양

### 8.1 종목 데이터 (StockData)

```python
{
    'code': str,           # 종목 코드 (예: "005930")
    'name': str,           # 종목명 (예: "삼성전자")
    'price': float,        # 현재가 (예: 70000)
    'open': float,         # 시가
    'high': float,         # 고가
    'low': float,          # 저가
    'close': float,        # 종가
    'volume': int,         # 거래량
    'amount': int,         # 거래대금
    'change_rate': float,  # 등락률 (%)
    'prev_high': float,    # 전일 고가
    'prev_low': float      # 전일 저가
}
```

### 8.2 선정 종목 데이터 (SelectedStock)

```python
{
    'code': str,           # 종목 코드
    'name': str,           # 종목명
    'price': float,        # 현재가
    'volume': int,         # 거래량
    'amount': int,         # 거래대금
    'change_rate': float,  # 등락률
    'score': int,          # 선정 점수 (0-16)
    'signals': {           # 발생 신호들
        'volume_surge': bool,
        'golden_cross': bool,
        'ma_20_above': bool,
        'volatility_breakout': bool,
        'macd_buy': bool,
        'stochastic_buy': bool,
        'obv_rising': bool,
        'support_at_ma': bool
    },
    'timestamp': datetime  # 선정 시각
}
```

### 8.3 포지션 데이터 (Position)

```python
{
    'name': str,           # 종목명
    'entry_price': float,  # 진입가
    'quantity': int,       # 보유 수량
    'highest_price': float,# 최고가
    'entry_time': datetime # 진입 시각
}
```

---

## 9. 오류 코드

| 코드 | 설명 | 처리 방법 |
|------|------|----------|
| E001 | API 연결 실패 | 재연결 시도 (최대 3회) |
| E002 | 설정 검증 실패 | 프로그램 종료 |
| E003 | 데이터 조회 실패 | 해당 종목 스킵 |
| E004 | 주문 실패 | 로그 기록, 알림 |
| E005 | 데이터베이스 연결 실패 | 재연결 시도 |
| E006 | 일일 손실 제한 도달 | 거래 중단 |

---

## 10. 성능 기준

| 항목 | 기준 | 측정 방법 |
|------|------|----------|
| 종목 선정 시간 | 30초 이내 (30개 종목) | time.time() 측정 |
| 지표 계산 시간 | 1초 이내 (단일 종목) | time.time() 측정 |
| 메모리 사용량 | 2GB 이하 | psutil 모니터링 |
| CPU 사용률 | 50% 이하 (4코어 기준) | psutil 모니터링 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 초기 프로그램 사양서 작성 | RedArrow Team |

---

**문서 끝**
