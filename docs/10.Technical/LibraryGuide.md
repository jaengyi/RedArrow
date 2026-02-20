# RedArrow 라이브러리 사용 가이드

## 개요

이 문서는 RedArrow 프로젝트에서 사용하는 주요 Python 라이브러리의 사용법을 설명합니다. 각 라이브러리의 핵심 기능과 프로젝트에서 어떻게 활용되는지 예제와 함께 설명합니다.

---

## 목차

1. [pandas - 데이터 분석](#1-pandas---데이터-분석)
2. [numpy - 수치 계산](#2-numpy---수치-계산)
3. [requests - HTTP 통신](#3-requests---http-통신)
4. [PyYAML - YAML 파싱](#4-pyyaml---yaml-파싱)
5. [python-dotenv - 환경 변수](#5-python-dotenv---환경-변수)
6. [APScheduler - 작업 스케줄링](#6-apscheduler---작업-스케줄링)
7. [pathlib - 파일 경로](#7-pathlib---파일-경로)
8. [logging - 로깅](#8-logging---로깅)
9. [re - 정규표현식](#9-re---정규표현식)

---

## 1. pandas - 데이터 분석

### 설치
```bash
pip install pandas
```

### 핵심 개념

pandas는 표 형태의 데이터를 다루는 Python 라이브러리입니다.

#### Series (1차원)
```python
import pandas as pd

# Series 생성
prices = pd.Series([100, 105, 103, 108, 110])
print(prices)
# 0    100
# 1    105
# 2    103
# 3    108
# 4    110
```

#### DataFrame (2차원)
```python
# DataFrame 생성
data = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'open': [100, 105, 103],
    'high': [107, 110, 108],
    'low': [99, 104, 101],
    'close': [105, 103, 108],
    'volume': [10000, 15000, 12000]
})
print(data)
```

### RedArrow에서의 활용

#### 이동평균 계산 (rolling)
```python
# src/indicators/technical_indicators.py에서 사용
def calculate_ma(self, data: pd.Series, period: int) -> pd.Series:
    """
    rolling(window=period): 이동 윈도우 생성
    .mean(): 윈도우 내 평균 계산

    예시 (period=3):
    데이터: [10, 12, 11, 13, 15]
    결과:   [NaN, NaN, 11, 12, 13]
    """
    return data.rolling(window=period).mean()
```

#### 지수이동평균 계산 (ewm)
```python
def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
    """
    ewm(span=period): 지수 가중 이동 윈도우
    - 최근 데이터에 더 높은 가중치 부여
    - adjust=False: 초기값 계산 방식
    """
    return data.ewm(span=period, adjust=False).mean()
```

#### DataFrame 필터링과 정렬
```python
# src/stock_selector/selector.py에서 사용
def filter_by_volume_amount(self, stock_data: pd.DataFrame, top_n: int):
    # 거래대금 기준 내림차순 정렬
    sorted_stocks = stock_data.sort_values('amount', ascending=False)

    # 상위 N개만 선택
    return sorted_stocks.head(top_n)
```

#### 유용한 메서드 정리

| 메서드 | 설명 | 예시 |
|--------|------|------|
| `rolling(n)` | n개 윈도우 생성 | `df['close'].rolling(20).mean()` |
| `ewm(span=n)` | 지수 가중 윈도우 | `df['close'].ewm(span=12).mean()` |
| `shift(n)` | n칸 이동 | `df['close'].shift(1)` (어제 값) |
| `diff()` | 차분 (변화량) | `df['close'].diff()` |
| `sort_values()` | 정렬 | `df.sort_values('amount', ascending=False)` |
| `head(n)` | 상위 n개 | `df.head(10)` |
| `iterrows()` | 행 순회 | `for idx, row in df.iterrows():` |

---

## 2. numpy - 수치 계산

### 설치
```bash
pip install numpy
```

### 핵심 개념

numpy는 고성능 수치 계산을 위한 라이브러리입니다.

```python
import numpy as np

# 배열 생성
arr = np.array([1, 2, 3, 4, 5])

# 기본 연산
print(arr.mean())   # 평균: 3.0
print(arr.std())    # 표준편차: 1.414...
print(arr.sum())    # 합계: 15
print(arr.max())    # 최대값: 5
print(arr.min())    # 최소값: 1
```

### RedArrow에서의 활용

```python
# 테스트 데이터 생성
test_data = pd.DataFrame({
    'close': np.random.randn(100).cumsum() + 100,  # 랜덤 워크
    'volume': np.random.randint(1000000, 10000000, 100)  # 랜덤 거래량
})
```

---

## 3. requests - HTTP 통신

### 설치
```bash
pip install requests
```

### 핵심 개념

requests는 HTTP 요청을 보내고 응답을 받는 라이브러리입니다.

#### GET 요청
```python
import requests

# 기본 GET 요청
response = requests.get('https://api.example.com/data')

# 파라미터 포함
response = requests.get(
    'https://api.example.com/data',
    params={'stock_code': '005930'},
    timeout=10
)

# 응답 처리
if response.status_code == 200:
    data = response.json()  # JSON → 딕셔너리
    print(data)
```

#### POST 요청
```python
# POST 요청 (데이터 전송)
response = requests.post(
    'https://api.example.com/order',
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer TOKEN'
    },
    json={
        'stock_code': '005930',
        'quantity': 10,
        'price': 70000
    },
    timeout=10
)
```

### RedArrow에서의 활용

```python
# src/data_collectors/broker_api.py에서 사용

def connect(self) -> bool:
    """OAuth 토큰 발급"""
    url = f"{self.base_url}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": self.app_key,
        "appsecret": self.app_secret
    }

    response = requests.post(url, headers=headers, json=body, timeout=10)

    if response.status_code == 200:
        result = response.json()
        self.access_token = result.get('access_token')
        return True
    return False
```

#### 응답 객체 속성

| 속성/메서드 | 설명 | 예시 |
|-------------|------|------|
| `status_code` | HTTP 상태 코드 | 200, 404, 500 |
| `json()` | JSON → 딕셔너리 | `response.json()` |
| `text` | 응답 텍스트 | `response.text` |
| `headers` | 응답 헤더 | `response.headers['Content-Type']` |

---

## 4. PyYAML - YAML 파싱

### 설치
```bash
pip install pyyaml
```

### 핵심 개념

YAML은 사람이 읽기 쉬운 설정 파일 형식입니다.

#### YAML 파일 읽기
```python
import yaml

# YAML 파일 읽기
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 값 접근
print(config['stock_selector']['top_volume_count'])  # 30
```

#### YAML 예시
```yaml
# config/config.yaml
stock_selector:
  top_volume_count: 30
  volume_surge_threshold: 2.0
  k_value: 0.5

risk_management:
  stop_loss_percent: 2.5
  take_profit_percent: 5.0
  max_positions: 5
```

### RedArrow에서의 활용

```python
# src/config/settings.py에서 사용

def __init__(self, config_path: str = None):
    # YAML 파일 로드
    with open(config_path, 'r', encoding='utf-8') as f:
        self.config = yaml.safe_load(f)

    # 값 접근
    top_volume = self.config.get('stock_selector', {}).get('top_volume_count', 30)
```

#### safe_load vs load

| 함수 | 설명 |
|------|------|
| `yaml.safe_load()` | 안전한 파싱 (권장) - 임의 코드 실행 방지 |
| `yaml.load()` | 모든 YAML 태그 지원 - 보안 취약점 가능성 |

---

## 5. python-dotenv - 환경 변수

### 설치
```bash
pip install python-dotenv
```

### 핵심 개념

.env 파일의 환경 변수를 Python에서 사용할 수 있게 합니다.

#### .env 파일
```env
# .env
SIMULATION_APP_KEY=PS12345abcdef
SIMULATION_APP_SECRET=xyz789secret
TRADING_MODE=simulation
```

#### Python에서 사용
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
app_key = os.getenv('SIMULATION_APP_KEY')
trading_mode = os.getenv('TRADING_MODE', 'simulation')  # 기본값 지정
```

### RedArrow에서의 활용

```python
# src/config/settings.py에서 사용

def __init__(self):
    # .env 파일 로드
    env_path = self.root_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)

@property
def app_key(self) -> str:
    if self.trading_mode == 'simulation':
        return os.getenv('SIMULATION_APP_KEY', '')
    else:
        return os.getenv('REAL_APP_KEY', '')
```

---

## 6. APScheduler - 작업 스케줄링

### 설치
```bash
pip install apscheduler
```

### 핵심 개념

특정 시간에 자동으로 함수를 실행하는 스케줄러입니다.

#### 기본 사용법
```python
from apscheduler.schedulers.background import BackgroundScheduler

# 스케줄러 생성
scheduler = BackgroundScheduler(timezone='Asia/Seoul')

# 작업 추가
def my_job():
    print("작업 실행!")

# 매일 16:00에 실행
scheduler.add_job(my_job, 'cron', hour=16, minute=0)

# 10분마다 실행
scheduler.add_job(my_job, 'interval', minutes=10)

# 스케줄러 시작
scheduler.start()
```

### RedArrow에서의 활용

```python
# src/main.py에서 사용

def run(self):
    # 스케줄러 설정
    scheduler = BackgroundScheduler(timezone='Asia/Seoul')

    # 매일 16:00에 일일 리포트 생성
    scheduler.add_job(generate_daily_report, 'cron', hour=16, minute=0)

    scheduler.start()
    self.logger.info("📅 일일 리포트 생성 스케줄러 시작 (매일 16:00)")
```

#### 트리거 타입

| 트리거 | 설명 | 예시 |
|--------|------|------|
| `cron` | 정해진 시간 | `hour=16, minute=0` (매일 16:00) |
| `interval` | 일정 간격 | `minutes=5` (5분마다) |
| `date` | 특정 날짜 | `run_date='2024-12-31'` |

---

## 7. pathlib - 파일 경로

### 기본 제공

Python 3.4+ 표준 라이브러리입니다.

### 핵심 개념

파일 경로를 객체로 다루는 현대적인 방법입니다.

```python
from pathlib import Path

# 현재 파일 경로
current_file = Path(__file__)

# 부모 디렉토리
parent_dir = current_file.parent

# 경로 연결 (/ 연산자)
config_path = parent_dir / 'config' / 'config.yaml'

# 파일 존재 확인
if config_path.exists():
    print("파일 존재")

# 디렉토리 생성
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)  # 이미 있으면 무시
```

### RedArrow에서의 활용

```python
# src/config/settings.py에서 사용

# 프로젝트 루트 찾기
self.root_dir = Path(__file__).parent.parent.parent

# 설정 파일 경로
config_path = self.root_dir / 'config' / 'config.yaml'

# .env 파일 경로
env_path = self.root_dir / '.env'
```

#### 전통적 방법 vs pathlib

```python
# 전통적 방법 (os.path)
import os
root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config = os.path.join(root, 'config', 'config.yaml')

# pathlib (권장)
from pathlib import Path
root = Path(__file__).parent.parent.parent
config = root / 'config' / 'config.yaml'
```

---

## 8. logging - 로깅

### 기본 제공

Python 표준 라이브러리입니다.

### 핵심 개념

프로그램 실행 기록을 남기는 시스템입니다.

```python
import logging

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 로그 출력
logger.debug("디버깅용 정보")      # 개발용 (기본 출력 안 함)
logger.info("일반 정보")           # 정상 동작
logger.warning("경고")             # 주의 필요
logger.error("에러")               # 오류 발생
logger.critical("치명적 오류")     # 심각한 오류
```

### RedArrow에서의 활용

```python
# src/main.py에서 사용

def setup_logging(config: Dict):
    log_dir = Path(config.get('log_dir', 'logs'))
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"redarrow_{datetime.now().strftime('%Y%m%d')}.log"

    # 파일 핸들러 (로그 파일 저장)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # 루트 로거에 핸들러 추가
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
```

#### 로그 레벨

| 레벨 | 숫자 | 용도 |
|------|------|------|
| DEBUG | 10 | 개발/디버깅용 상세 정보 |
| INFO | 20 | 정상 동작 기록 |
| WARNING | 30 | 주의 필요 상황 |
| ERROR | 40 | 오류 발생 |
| CRITICAL | 50 | 심각한 오류 |

---

## 9. re - 정규표현식

### 기본 제공

Python 표준 라이브러리입니다.

### 핵심 개념

문자열에서 특정 패턴을 찾는 강력한 도구입니다.

#### 기본 문법

| 패턴 | 의미 | 예시 |
|------|------|------|
| `\d` | 숫자 1개 | `\d` → "1", "9" |
| `\d+` | 숫자 1개 이상 | `\d+` → "123" |
| `.` | 아무 문자 1개 | `.` → "a", "1" |
| `.+` | 아무 문자 1개 이상 | `.+` → "hello" |
| `()` | 그룹 (추출용) | `(\d+)` |
| `[]` | 문자 집합 | `[0-9]` → 숫자 |

#### 기본 사용법

```python
import re

text = "2024-01-15 10:30:00 - 삼성전자 100주 @ 70,000원"

# 패턴 컴파일 (성능 향상)
pattern = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})")

# 패턴 검색
match = pattern.search(text)
if match:
    print(match.group(1))  # "2024-01-15"
    print(match.group(2))  # "10:30:00"
```

### RedArrow에서의 활용

```python
# src/reporter/report_generator.py에서 사용

# 매수 로그 패턴
BUY_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - .+ - INFO - "
    r"✅ 매수 주문 접수 성공: (.+?) (\d+)주 @ ([\d,]+)원"
)

# 로그 파싱
for line in log_file:
    m = BUY_PATTERN.search(line)
    if m:
        time = m.group(1)       # 타임스탬프
        stock_name = m.group(2) # 종목명
        quantity = m.group(3)   # 수량
        price = m.group(4)      # 가격
```

#### 정규표현식 테스트

온라인 테스트 도구: https://regex101.com/

---

## 요약

| 라이브러리 | 용도 | RedArrow 활용 |
|------------|------|---------------|
| pandas | 데이터 분석 | 기술적 지표 계산, 종목 필터링 |
| numpy | 수치 계산 | 테스트 데이터 생성 |
| requests | HTTP 통신 | 증권사 API 호출 |
| PyYAML | YAML 파싱 | 설정 파일 로드 |
| python-dotenv | 환경 변수 | API 키 로드 |
| APScheduler | 스케줄링 | 일일 리포트 자동 생성 |
| pathlib | 파일 경로 | 설정 파일, 로그 파일 경로 |
| logging | 로깅 | 거래 기록, 에러 로그 |
| re | 정규표현식 | 로그 파일 파싱 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-02-20 | 1.0 | 최초 작성 |
