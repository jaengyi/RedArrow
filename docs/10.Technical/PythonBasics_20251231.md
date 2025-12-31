# RedArrow - Python 기초 기술 가이드

## 문서 정보
- **작성일**: 2025-12-31
- **최종 수정일**: 2025-12-31
- **버전**: 1.0
- **작성자**: RedArrow Team
- **대상**: Python 초보자 및 RedArrow 프로젝트 입문자

---

## 목차
1. [Python 기초](#1-python-기초)
2. [RedArrow 프로젝트에서 사용하는 Python 문법](#2-redarrow-프로젝트에서-사용하는-python-문법)
3. [주요 라이브러리 사용법](#3-주요-라이브러리-사용법)
4. [객체지향 프로그래밍 (OOP)](#4-객체지향-프로그래밍-oop)
5. [파일 및 데이터 처리](#5-파일-및-데이터-처리)
6. [RedArrow 코드 읽기](#6-redarrow-코드-읽기)
7. [디버깅 및 테스트](#7-디버깅-및-테스트)

---

## 1. Python 기초

### 1.1 Python이란?

Python은 읽기 쉽고 배우기 쉬운 프로그래밍 언어입니다. RedArrow 프로젝트는 Python 3.11 이상을 사용합니다.

### 1.2 Python 설치 확인

```bash
# 터미널에서 Python 버전 확인
python --version
# 또는
python3 --version

# 예상 출력: Python 3.11.x
```

### 1.3 기본 데이터 타입

#### 1.3.1 숫자 (Numbers)
```python
# 정수 (int)
price = 70000
quantity = 10

# 실수 (float)
profit_rate = 2.5
loss_percent = -1.3

# 사칙연산
total = price * quantity        # 곱셈: 700000
half_price = price / 2          # 나눗셈: 35000.0
profit = price * (profit_rate / 100)  # 1750.0
```

#### 1.3.2 문자열 (Strings)
```python
# 문자열 생성
stock_name = "삼성전자"
stock_code = "005930"

# 문자열 연결
message = stock_name + " (" + stock_code + ")"
# 결과: "삼성전자 (005930)"

# f-string (포맷팅) - Python 3.6+
message = f"{stock_name} ({stock_code})"
# 결과: "삼성전자 (005930)"

# 문자열 메서드
upper_code = stock_code.upper()     # "005930"
lower_name = stock_name.lower()     # "삼성전자"
```

#### 1.3.3 불린 (Boolean)
```python
# True 또는 False
is_market_open = True
has_position = False

# 비교 연산
price = 70000
is_expensive = price > 50000  # True
is_cheap = price < 30000      # False

# 논리 연산
can_buy = is_market_open and not has_position
# True and True = True
```

#### 1.3.4 리스트 (Lists)
```python
# 리스트 생성
prices = [70000, 71000, 69500, 70500]
stock_codes = ["005930", "000660", "051910"]

# 인덱싱 (0부터 시작)
first_price = prices[0]      # 70000
last_price = prices[-1]      # 70500

# 슬라이싱
first_two = prices[0:2]      # [70000, 71000]
last_two = prices[-2:]       # [69500, 70500]

# 리스트 메서드
prices.append(72000)         # 끝에 추가
prices.insert(0, 68000)      # 특정 위치에 삽입
prices.remove(69500)         # 값 제거
length = len(prices)         # 리스트 길이
```

#### 1.3.5 딕셔너리 (Dictionaries)
```python
# 딕셔너리 생성 (key: value 쌍)
stock = {
    'code': '005930',
    'name': '삼성전자',
    'price': 70000,
    'volume': 10000000
}

# 값 접근
code = stock['code']              # '005930'
name = stock.get('name')          # '삼성전자'
safe_value = stock.get('missing', 'default')  # 'default'

# 값 추가/수정
stock['change_rate'] = 1.5        # 추가
stock['price'] = 71000            # 수정

# 딕셔너리 메서드
keys = stock.keys()               # dict_keys(['code', 'name', ...])
values = stock.values()           # dict_values(['005930', '삼성전자', ...])
items = stock.items()             # dict_items([('code', '005930'), ...])
```

### 1.4 제어문

#### 1.4.1 조건문 (if-elif-else)
```python
price = 70000

if price > 80000:
    print("고가")
elif price > 60000:
    print("중가")
else:
    print("저가")
# 출력: "중가"

# 한 줄 조건문
status = "매수" if price > 65000 else "대기"
```

#### 1.4.2 반복문 (for, while)
```python
# for 반복문
stock_codes = ["005930", "000660", "051910"]

for code in stock_codes:
    print(f"종목 코드: {code}")

# 인덱스와 함께 반복
for index, code in enumerate(stock_codes):
    print(f"{index}: {code}")

# range 사용
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# while 반복문
count = 0
while count < 5:
    print(count)
    count += 1

# break와 continue
for price in [70000, 0, 71000, 72000]:
    if price == 0:
        continue  # 건너뛰기
    if price > 71500:
        break     # 중단
    print(price)
```

### 1.5 함수 (Functions)

#### 1.5.1 함수 정의
```python
# 기본 함수
def greet():
    print("안녕하세요!")

greet()  # 호출
# 출력: "안녕하세요!"

# 매개변수가 있는 함수
def calculate_profit(price, quantity):
    return price * quantity

result = calculate_profit(70000, 10)
print(result)  # 700000

# 기본값 매개변수
def calculate_rate(current, previous, decimal=2):
    rate = ((current - previous) / previous) * 100
    return round(rate, decimal)

rate1 = calculate_rate(71000, 70000)      # 1.43
rate2 = calculate_rate(71000, 70000, 4)   # 1.4286
```

#### 1.5.2 타입 힌트 (Type Hints)
```python
# RedArrow 프로젝트에서 사용하는 방식
from typing import Dict, List, Optional

def calculate_average(prices: List[float]) -> float:
    """가격 리스트의 평균을 계산합니다."""
    return sum(prices) / len(prices)

def get_stock_info(code: str) -> Dict[str, any]:
    """종목 정보를 반환합니다."""
    return {
        'code': code,
        'name': '삼성전자',
        'price': 70000
    }

def find_stock(code: str) -> Optional[Dict]:
    """종목을 찾습니다. 없으면 None 반환."""
    if code == "005930":
        return {'name': '삼성전자'}
    return None
```

---

## 2. RedArrow 프로젝트에서 사용하는 Python 문법

### 2.1 모듈과 패키지

#### 2.1.1 import 문
```python
# 전체 모듈 import
import pandas

# 특정 클래스/함수 import
from pandas import DataFrame

# 별칭 사용
import pandas as pd
import numpy as np

# 프로젝트 내부 모듈 import
from src.indicators import TechnicalIndicators
from src.stock_selector import StockSelector
```

#### 2.1.2 __init__.py 파일
```python
# src/indicators/__init__.py
from .technical_indicators import TechnicalIndicators

__all__ = ['TechnicalIndicators']

# 이렇게 하면 다음과 같이 사용 가능:
# from src.indicators import TechnicalIndicators
```

### 2.2 클래스 (Classes)

#### 2.2.1 기본 클래스
```python
class Stock:
    """주식 클래스"""

    def __init__(self, code, name, price):
        """초기화 메서드"""
        self.code = code
        self.name = name
        self.price = price

    def get_info(self):
        """정보 반환 메서드"""
        return f"{self.name} ({self.code}): {self.price:,}원"

    def update_price(self, new_price):
        """가격 업데이트 메서드"""
        self.price = new_price

# 사용 예시
samsung = Stock("005930", "삼성전자", 70000)
print(samsung.get_info())
# 출력: "삼성전자 (005930): 70,000원"

samsung.update_price(71000)
print(samsung.price)  # 71000
```

#### 2.2.2 프로퍼티 (Properties)
```python
class Settings:
    """설정 클래스"""

    def __init__(self):
        self._api_key = None

    @property
    def api_key(self):
        """API 키 getter"""
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        """API 키 setter"""
        if len(value) < 10:
            raise ValueError("API 키가 너무 짧습니다")
        self._api_key = value

# 사용 예시
settings = Settings()
settings.api_key = "my_secret_key_12345"
print(settings.api_key)
```

### 2.3 데코레이터 (Decorators)

#### 2.3.1 기본 데코레이터
```python
def log_function_call(func):
    """함수 호출을 로그로 기록하는 데코레이터"""
    def wrapper(*args, **kwargs):
        print(f"함수 {func.__name__} 호출")
        result = func(*args, **kwargs)
        print(f"함수 {func.__name__} 완료")
        return result
    return wrapper

@log_function_call
def calculate_profit(price, quantity):
    return price * quantity

result = calculate_profit(70000, 10)
# 출력:
# 함수 calculate_profit 호출
# 함수 calculate_profit 완료
```

#### 2.3.2 @property 데코레이터
```python
class RiskManager:
    def __init__(self, config):
        self._stop_loss_percent = config.get('stop_loss_percent', 2.5)

    @property
    def stop_loss_percent(self):
        """손절 퍼센트 반환"""
        return self._stop_loss_percent

# 사용
rm = RiskManager({'stop_loss_percent': 3.0})
print(rm.stop_loss_percent)  # 3.0
```

### 2.4 예외 처리

```python
def divide_numbers(a, b):
    try:
        result = a / b
        return result
    except ZeroDivision error:
        print("0으로 나눌 수 없습니다")
        return None
    except TypeError:
        print("숫자만 입력 가능합니다")
        return None
    finally:
        print("계산 완료")

# RedArrow에서 사용하는 패턴
def connect_to_api():
    try:
        # API 연결 시도
        api.connect()
        return True
    except ConnectionError as e:
        logger.error(f"API 연결 실패: {e}")
        return False
    except Exception as e:
        logger.critical(f"예상치 못한 오류: {e}")
        return False
```

---

## 3. 주요 라이브러리 사용법

### 3.1 pandas (데이터 처리)

#### 3.1.1 DataFrame 기초
```python
import pandas as pd

# DataFrame 생성
data = {
    'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
    'price': [70000, 71000, 69500],
    'volume': [1000000, 1200000, 950000]
}
df = pd.DataFrame(data)

print(df)
#         date  price   volume
# 0 2025-01-01  70000  1000000
# 1 2025-01-02  71000  1200000
# 2 2025-01-03  69500   950000

# 컬럼 접근
prices = df['price']        # Series
# 또는
prices = df.price

# 행 접근
first_row = df.iloc[0]      # 인덱스로 접근
last_row = df.iloc[-1]

# 조건 필터링
high_price_df = df[df['price'] > 70000]
```

#### 3.1.2 Series 기초
```python
import pandas as pd

# Series 생성
prices = pd.Series([70000, 71000, 69500, 70500])

print(prices)
# 0    70000
# 1    71000
# 2    69500
# 3    70500
# dtype: int64

# Series 연산
mean_price = prices.mean()          # 평균: 70250.0
max_price = prices.max()            # 최대: 71000
min_price = prices.min()            # 최소: 69500

# 슬라이싱
first_two = prices[0:2]
# 0    70000
# 1    71000
```

#### 3.1.3 RedArrow에서 사용하는 pandas 패턴
```python
import pandas as pd

# 과거 가격 데이터
price_data = pd.Series([70000, 70500, 69800, 71000, 70300])

# 이동평균 계산
ma_5 = price_data.rolling(window=5).mean()
# 0       NaN
# 1       NaN
# 2       NaN
# 3       NaN
# 4    70320.0

# 전일 대비 변화
price_change = price_data.diff()
# 0      NaN
# 1    500.0
# 2   -700.0
# 3   1200.0
# 4   -700.0

# DataFrame에서 데이터 필터링
stock_data = pd.DataFrame({
    'code': ['005930', '000660', '051910'],
    'price': [70000, 120000, 400000],
    'volume': [10000000, 5000000, 2000000]
})

# 가격이 100000 이상인 종목만 선택
expensive_stocks = stock_data[stock_data['price'] >= 100000]
```

### 3.2 numpy (수치 계산)

```python
import numpy as np

# 배열 생성
prices = np.array([70000, 71000, 69500, 70500])

# 기본 통계
mean = np.mean(prices)          # 평균
std = np.std(prices)            # 표준편차
max_val = np.max(prices)        # 최대값
min_val = np.min(prices)        # 최소값

# 배열 연산
prices_usd = prices / 1300      # 모든 요소에 동일 연산
change = prices[1:] - prices[:-1]  # 전일 대비 변화

# RedArrow에서 사용하는 패턴
# 변동률 계산
returns = np.diff(prices) / prices[:-1] * 100
```

### 3.3 PyYAML (설정 파일 읽기)

```python
import yaml

# YAML 파일 읽기
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 설정 값 접근
top_volume_count = config['stock_selector']['top_volume_count']
stop_loss_percent = config['risk_management']['stop_loss_percent']

print(f"거래대금 상위 {top_volume_count}개 종목 선정")
print(f"손절 기준: {stop_loss_percent}%")
```

### 3.4 python-dotenv (환경 변수)

```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 접근
api_key = os.getenv('APP_KEY')
app_secret = os.getenv('APP_SECRET')
trading_mode = os.getenv('TRADING_MODE', 'simulation')  # 기본값 지정

print(f"API 키: {api_key[:10]}...")
print(f"거래 모드: {trading_mode}")
```

---

## 4. 객체지향 프로그래밍 (OOP)

### 4.1 클래스와 객체

#### 4.1.1 RedArrow의 TechnicalIndicators 클래스 이해하기
```python
class TechnicalIndicators:
    """기술적 지표를 계산하는 클래스"""

    def __init__(self):
        """생성자: 객체가 생성될 때 호출됩니다"""
        pass  # 이 클래스는 특별한 초기화가 필요 없음

    def calculate_ma(self, data, period):
        """이동평균을 계산하는 메서드"""
        return data.rolling(window=period).mean()

    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """MACD를 계산하는 메서드"""
        fast_ema = data.ewm(span=fast).mean()
        slow_ema = data.ewm(span=slow).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal).mean()

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': macd_line - signal_line
        }

# 사용 방법
indicators = TechnicalIndicators()  # 객체 생성

# 샘플 데이터
import pandas as pd
prices = pd.Series([70000, 70500, 69800, 71000, 70300])

# 이동평균 계산
ma_5 = indicators.calculate_ma(prices, 5)

# MACD 계산
macd_result = indicators.calculate_macd(prices)
print(macd_result['macd'])
```

#### 4.1.2 StockSelector 클래스 이해하기
```python
class StockSelector:
    """종목을 선정하는 클래스"""

    def __init__(self, config):
        """
        생성자
        config: 설정 딕셔너리 (YAML에서 로드)
        """
        self.config = config
        self.indicators = TechnicalIndicators()
        self.top_volume_count = config.get('top_volume_count', 30)

    def filter_by_volume_amount(self, stock_data, top_n=None):
        """거래대금 상위 종목 필터링"""
        if top_n is None:
            top_n = self.top_volume_count

        # 거래대금 기준 정렬
        sorted_stocks = stock_data.sort_values('amount', ascending=False)
        return sorted_stocks.head(top_n)

    def select_stocks(self, stock_data, price_history):
        """메인 종목 선정 로직"""
        # 1. 거래대금 상위 종목 필터링
        top_stocks = self.filter_by_volume_amount(stock_data)

        selected = []
        for _, stock in top_stocks.iterrows():
            score = 0
            # ... 점수 계산 로직

            if score >= 5:
                selected.append(stock)

        return selected

# 사용 방법
config = {'top_volume_count': 30, 'volume_surge_threshold': 2.0}
selector = StockSelector(config)

# 종목 데이터 (DataFrame)
stock_data = pd.DataFrame(...)
price_history = {...}

# 종목 선정
selected_stocks = selector.select_stocks(stock_data, price_history)
```

### 4.2 상속 (Inheritance)

```python
from abc import ABC, abstractmethod

class BrokerAPI(ABC):
    """증권사 API 추상 클래스"""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def connect(self):
        """API 연결 - 하위 클래스에서 반드시 구현해야 함"""
        pass

    @abstractmethod
    def get_stock_price(self, code):
        """주가 조회 - 하위 클래스에서 반드시 구현해야 함"""
        pass

class KoreaInvestmentAPI(BrokerAPI):
    """한국투자증권 API 구체 클래스"""

    def connect(self):
        """한국투자증권 API 연결 구현"""
        print("한국투자증권 API에 연결 중...")
        # 실제 연결 로직
        return True

    def get_stock_price(self, code):
        """한국투자증권 API로 주가 조회 구현"""
        print(f"종목 {code} 조회 중...")
        # 실제 조회 로직
        return 70000

# 사용
api = KoreaInvestmentAPI({'api_key': 'xxx'})
api.connect()
price = api.get_stock_price('005930')
```

---

## 5. 파일 및 데이터 처리

### 5.1 파일 읽기/쓰기

#### 5.1.1 텍스트 파일
```python
# 파일 읽기
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 파일 쓰기
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("종목: 삼성전자\n")
    f.write("가격: 70000\n")

# 파일에 추가
with open('output.txt', 'a', encoding='utf-8') as f:
    f.write("거래량: 10000000\n")
```

#### 5.1.2 CSV 파일 (pandas 사용)
```python
import pandas as pd

# CSV 읽기
df = pd.read_csv('stocks.csv')

# CSV 쓰기
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
```

#### 5.1.3 YAML 파일
```python
import yaml

# YAML 읽기
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# YAML 쓰기
data = {
    'stock_selector': {
        'top_volume_count': 30,
        'volume_surge_threshold': 2.0
    }
}

with open('new_config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True)
```

### 5.2 경로 처리

```python
from pathlib import Path

# 현재 파일의 경로
current_file = Path(__file__)
print(current_file)
# 출력: /Users/xxx/RedArrow/src/main.py

# 부모 디렉토리
parent_dir = current_file.parent
print(parent_dir)
# 출력: /Users/xxx/RedArrow/src

# 프로젝트 루트
root_dir = current_file.parent.parent
print(root_dir)
# 출력: /Users/xxx/RedArrow

# 경로 결합
config_path = root_dir / 'config' / 'config.yaml'
print(config_path)
# 출력: /Users/xxx/RedArrow/config/config.yaml

# 파일 존재 확인
if config_path.exists():
    print("설정 파일이 존재합니다")

# 디렉토리 생성
logs_dir = root_dir / 'logs'
logs_dir.mkdir(exist_ok=True)  # exist_ok=True: 이미 존재해도 오류 없음
```

---

## 6. RedArrow 코드 읽기

### 6.1 main.py 이해하기

```python
# src/main.py 주요 부분 설명

# 1. 모듈 import
import sys
from pathlib import Path

# 프로젝트 모듈 import
from src.config import Settings
from src.stock_selector import StockSelector
from src.risk_manager import RiskManager

# 2. 로깅 설정 함수
def setup_logging(config):
    """
    로깅 시스템을 초기화하는 함수
    config: 로깅 설정 딕셔너리
    """
    # 로그 디렉토리 생성
    log_dir = Path(config.get('log_dir', 'logs'))
    log_dir.mkdir(exist_ok=True)

    # ... 로깅 설정
    return logger

# 3. RedArrowSystem 클래스
class RedArrowSystem:
    """메인 시스템 클래스"""

    def __init__(self):
        """시스템 초기화"""
        # 설정 로드
        self.settings = Settings()

        # 로깅 설정
        self.logger = setup_logging(self.settings.logging_config)

        # 모듈 초기화
        self.stock_selector = StockSelector(self.settings.stock_selector_config)
        self.risk_manager = RiskManager(self.settings.risk_management_config)

    def run(self):
        """메인 실행 함수"""
        try:
            # 1. 시장 개장 확인
            if not self.is_market_open():
                return

            # 2. 데이터 수집
            market_data = self.collect_market_data()

            # 3. 종목 선정
            selected_stocks = self.select_stocks(market_data)

            # 4. 매매 실행 (시뮬레이션)
            for stock in selected_stocks:
                self.execute_trade(stock)

            # 5. 포지션 모니터링
            self.monitor_positions()

        except Exception as e:
            self.logger.error(f"오류 발생: {e}")

# 4. main 함수
def main():
    """프로그램 진입점"""
    print("RedArrow 시작")
    system = RedArrowSystem()
    system.run()

# 5. 실행 부분
if __name__ == "__main__":
    main()
```

**설명**:
- `if __name__ == "__main__":`: 이 파일이 직접 실행될 때만 main() 함수 호출
- `try-except`: 오류 처리
- `self`: 클래스 내에서 자기 자신을 가리키는 변수

### 6.2 Settings 클래스 이해하기

```python
# src/config/settings.py 주요 부분

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    """설정 관리 클래스"""

    def __init__(self, config_path=None):
        """초기화"""
        # 1. 프로젝트 루트 찾기
        self.root_dir = Path(__file__).parent.parent.parent

        # 2. .env 파일 로드
        env_path = self.root_dir / '.env'
        load_dotenv(env_path)

        # 3. config.yaml 로드
        if config_path is None:
            config_path = self.root_dir / 'config' / 'config.yaml'

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    @property
    def broker_type(self):
        """증권사 타입 반환"""
        return os.getenv('BROKER_TYPE', 'koreainvestment')

    @property
    def stop_loss_percent(self):
        """손절 퍼센트 반환"""
        # 환경 변수 우선, 없으면 config.yaml 값 사용
        env_value = os.getenv('STOP_LOSS_PERCENT')
        if env_value:
            return float(env_value)
        return self.config['risk_management']['stop_loss_percent']

# 사용 예시
settings = Settings()
print(settings.broker_type)          # "koreainvestment"
print(settings.stop_loss_percent)    # 2.5
```

**설명**:
- `@property`: 메서드를 속성처럼 사용 가능하게 함
- `os.getenv()`: 환경 변수 가져오기
- `Path(__file__)`: 현재 파일의 경로

---

## 7. 디버깅 및 테스트

### 7.1 print 디버깅

```python
# 변수 값 확인
price = 70000
print(f"가격: {price}")

# 타입 확인
print(f"가격 타입: {type(price)}")

# 리스트/딕셔너리 내용 확인
stock = {'code': '005930', 'price': 70000}
print(f"종목 정보: {stock}")

# 조건 확인
if price > 65000:
    print("조건 만족")
else:
    print("조건 불만족")
```

### 7.2 로깅

```python
import logging

# 로거 생성
logger = logging.getLogger(__name__)

# 로그 레벨별 사용
logger.debug("상세 디버깅 정보")      # DEBUG
logger.info("일반 정보")             # INFO
logger.warning("경고")               # WARNING
logger.error("오류 발생")            # ERROR
logger.critical("치명적 오류")       # CRITICAL

# 변수 포함
price = 70000
logger.info(f"현재 가격: {price:,}원")
```

### 7.3 간단한 테스트

```python
# 함수 테스트
def calculate_average(prices):
    return sum(prices) / len(prices)

# 테스트
test_prices = [70000, 71000, 69000]
result = calculate_average(test_prices)
expected = 70000

if result == expected:
    print("✅ 테스트 성공")
else:
    print(f"❌ 테스트 실패: 기대값 {expected}, 결과값 {result}")
```

### 7.4 IPython / Jupyter 사용

```python
# IPython에서 실행
# pip install ipython

# 터미널에서
# $ ipython

# 코드 실행 및 테스트
from src.indicators import TechnicalIndicators
import pandas as pd

indicators = TechnicalIndicators()
prices = pd.Series([70000, 71000, 69000, 70500])

# 이동평균 계산
ma = indicators.calculate_ma(prices, 3)
print(ma)

# 변수 확인
ma?  # 도움말 표시
%timeit indicators.calculate_ma(prices, 3)  # 실행 시간 측정
```

---

## 8. 자주 사용하는 패턴

### 8.1 리스트 컴프리헨션

```python
# 일반 방법
prices = [70000, 71000, 69000, 70500]
high_prices = []
for price in prices:
    if price > 70000:
        high_prices.append(price)

# 리스트 컴프리헨션 (간결함)
high_prices = [price for price in prices if price > 70000]
# 결과: [71000, 70500]

# RedArrow에서 사용하는 예
stock_codes = ["005930", "000660", "051910"]
codes_with_0 = [code for code in stock_codes if '0' in code]
```

### 8.2 딕셔너리 컴프리헨션

```python
# 주식 코드: 가격 매핑
stocks = [
    {'code': '005930', 'price': 70000},
    {'code': '000660', 'price': 120000}
]

price_dict = {stock['code']: stock['price'] for stock in stocks}
# 결과: {'005930': 70000, '000660': 120000}
```

### 8.3 enumerate 사용

```python
stock_codes = ["005930", "000660", "051910"]

for index, code in enumerate(stock_codes):
    print(f"{index + 1}. {code}")

# 출력:
# 1. 005930
# 2. 000660
# 3. 051910
```

### 8.4 zip 사용

```python
codes = ["005930", "000660"]
names = ["삼성전자", "SK하이닉스"]
prices = [70000, 120000]

for code, name, price in zip(codes, names, prices):
    print(f"{name}({code}): {price:,}원")

# 출력:
# 삼성전자(005930): 70,000원
# SK하이닉스(000660): 120,000원
```

---

## 9. 학습 팁

### 9.1 코드 읽는 순서
1. `README.md` - 프로젝트 개요 파악
2. `requirements.txt` - 사용하는 라이브러리 확인
3. `src/main.py` - 메인 실행 흐름 이해
4. `src/config/settings.py` - 설정 관리 방법 이해
5. 각 모듈 순서대로 읽기

### 9.2 실습 방법
1. 가상환경 생성 및 활성화
2. 의존성 설치
3. IPython이나 Jupyter에서 코드 한 줄씩 실행
4. print() 문으로 변수 값 확인
5. 간단한 수정 후 재실행

### 9.3 참고 자료
- **Python 공식 문서**: https://docs.python.org/ko/3/
- **pandas 문서**: https://pandas.pydata.org/docs/
- **Real Python**: https://realpython.com/
- **점프 투 파이썬**: https://wikidocs.net/book/1

---

## 10. 연습 문제

### 문제 1: 간단한 이동평균 계산
```python
# 다음 가격 데이터의 3일 이동평균을 계산하세요
prices = [70000, 71000, 69500, 70500, 72000]

# 힌트: 슬라이싱과 sum(), len() 사용
```

### 문제 2: 종목 필터링
```python
# 가격이 100000 이상인 종목만 필터링하세요
stocks = [
    {'code': '005930', 'price': 70000},
    {'code': '000660', 'price': 120000},
    {'code': '051910', 'price': 400000}
]

# 힌트: 리스트 컴프리헨션 사용
```

### 문제 3: 클래스 만들기
```python
# Stock 클래스를 만들어 보세요
# - 속성: code, name, price
# - 메서드: get_info() - "종목명(코드): 가격원" 형식으로 반환

# 예시:
# samsung = Stock("005930", "삼성전자", 70000)
# print(samsung.get_info())
# 출력: "삼성전자(005930): 70,000원"
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-12-31 | 1.0 | 초기 Python 기초 가이드 작성 | RedArrow Team |

---

**문서 끝**
