"""
증권사 API 연동 모듈

실제 증권사 API를 연동하여 데이터를 수집하고 주문을 체결합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
import pandas as pd
import requests
import hashlib
import time
import json
import os
from datetime import datetime
from pathlib import Path
import logging
import threading
from functools import wraps


class RateLimiter:
    """
    Thread-safe Rate Limiter (Token Bucket 방식)

    한국투자증권 API는 초당 약 2건 제한이 있음.
    안전하게 0.5초 간격(초당 2건)으로 API 호출을 제한함.
    """

    def __init__(self, min_interval: float = 0.5):
        """
        Args:
            min_interval: API 호출 최소 간격 (초). 기본 0.5초 = 초당 2건
        """
        self.min_interval = min_interval
        self.last_call_time = 0.0
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def wait(self):
        """다음 API 호출까지 필요한 시간만큼 대기"""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_call_time

            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                time.sleep(wait_time)

            self.last_call_time = time.time()

    def acquire(self) -> float:
        """
        Rate limit 토큰 획득 (대기 후 반환)

        Returns:
            실제 대기 시간 (초)
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_call_time
            wait_time = 0.0

            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                time.sleep(wait_time)

            self.last_call_time = time.time()
            return wait_time


class BrokerAPI(ABC):
    """증권사 API 추상 클래스"""

    def __init__(self, config: Dict):
        """
        초기화

        Args:
            config: API 설정 (app_key, app_secret, account_number 등)
        """
        self.config = config
        self.is_connected = False
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def connect(self) -> bool:
        """
        API 연결

        Returns:
            연결 성공 여부
        """
        pass

    @abstractmethod
    def disconnect(self):
        """API 연결 해제"""
        pass

    @abstractmethod
    def get_top_volume_stocks(self, count: int = 30) -> pd.DataFrame:
        """
        거래대금 상위 종목 조회

        Args:
            count: 조회할 종목 수

        Returns:
            종목 데이터 (DataFrame)
                컬럼: code, name, price, volume, amount, change_rate 등
        """
        pass

    @abstractmethod
    def get_stock_price(self, stock_code: str) -> Dict:
        """
        개별 종목 현재가 조회

        Args:
            stock_code: 종목 코드

        Returns:
            종목 정보 딕셔너리
        """
        pass

    @abstractmethod
    def get_historical_data(
        self,
        stock_code: str,
        days: int = 30
    ) -> pd.DataFrame:
        """
        과거 가격 데이터 조회

        Args:
            stock_code: 종목 코드
            days: 조회 기간 (일)

        Returns:
            과거 가격 데이터 (DataFrame)
                컬럼: open, high, low, close, volume
                인덱스: datetime
        """
        pass

    @abstractmethod
    def get_minute_data(
        self,
        stock_code: str,
        interval: int = 1
    ) -> pd.DataFrame:
        """
        분봉 데이터 조회

        Args:
            stock_code: 종목 코드
            interval: 분봉 간격 (1, 3, 5, 10 등)

        Returns:
            분봉 데이터 (DataFrame)
        """
        pass

    @abstractmethod
    def get_order_book(self, stock_code: str) -> Dict:
        """
        호가창 데이터 조회

        Args:
            stock_code: 종목 코드

        Returns:
            호가창 정보 딕셔너리
                {
                    'bid': [매수호가 리스트],
                    'ask': [매도호가 리스트],
                    'bid_volume': [매수잔량 리스트],
                    'ask_volume': [매도잔량 리스트]
                }
        """
        pass

    @abstractmethod
    def place_buy_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """
        매수 주문

        Args:
            stock_code: 종목 코드
            quantity: 주문 수량
            price: 주문 가격 (None이면 시장가)

        Returns:
            주문 결과 딕셔너리
        """
        pass

    @abstractmethod
    def place_sell_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """
        매도 주문

        Args:
            stock_code: 종목 코드
            quantity: 주문 수량
            price: 주문 가격 (None이면 시장가)

        Returns:
            주문 결과 딕셔너리
        """
        pass

    @abstractmethod
    def get_account_balance(self) -> Dict:
        """
        계좌 잔고 조회

        Returns:
            잔고 정보 딕셔너리
        """
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """
        보유 종목 조회

        Returns:
            보유 종목 리스트
        """
        pass


class KoreaInvestmentAPI(BrokerAPI):
    """
    한국투자증권 API 구현 클래스

    공식 문서: https://apiportal.koreainvestment.com/
    """

    def __init__(self, config: Dict):
        super().__init__(config)

        # API 엔드포인트 설정
        self.app_key = config.get('app_key')
        self.app_secret = config.get('app_secret')
        self.account_number = config.get('account_number', '').replace('-', '')

        # 거래 모드 명시적으로 설정
        self.trading_mode = config.get('trading_mode', 'simulation')

        # 모의투자/실전투자 여부 판단 (trading_mode 우선, 계좌번호로 이중 체크)
        self.is_simulation = (self.trading_mode == 'simulation') or self.account_number.startswith('5')

        # 서버 URL 설정
        default_url = 'https://openapivts.koreainvestment.com:29443' if self.is_simulation else 'https://openapi.koreainvestment.com:9443'
        self.base_url = config.get('base_url', default_url)

        # 계좌번호 파싱 (앞 8자리-뒷자리)
        if len(self.account_number) >= 8:
            self.account_prefix = self.account_number[:8]
            self.account_suffix = self.account_number[8:] if len(self.account_number) > 8 else '01'
        else:
            self.account_prefix = self.account_number
            self.account_suffix = '01'

        self.access_token = None
        self.token_expiry = None

        # 토큰 저장 파일 경로
        self.token_file = Path(__file__).parent.parent.parent / '.token_cache.json'

        # 주요 종목 리스트 파일 경로
        self.stock_list_file = Path(__file__).parent.parent.parent / 'config' / 'stock_list.json'
        self._load_stock_list()

        # Rate Limiter 초기화 (초당 2건 = 0.5초 간격)
        self._rate_limiter = RateLimiter(min_interval=0.5)

    def _load_stock_list(self):
        """주요 종목 리스트 로드"""
        try:
            with open(self.stock_list_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stock_list = data.get('stocks', [])
                self.logger.info(f"✅ 주요 종목 리스트 로드: {len(self.stock_list)}개 종목")
        except Exception as e:
            self.logger.warning(f"종목 리스트 로드 실패: {e}")
            self.stock_list = []

    def _load_token(self) -> bool:
        """저장된 토큰 로드"""
        try:
            if not self.token_file.exists():
                return False

            with open(self.token_file, 'r') as f:
                token_data = json.load(f)

            # 토큰 유효성 확인
            if token_data.get('app_key') != self.app_key:
                self.logger.info("저장된 토큰의 app_key가 다릅니다")
                return False

            expiry = token_data.get('expiry', 0)
            # 만료 5분 전이면 갱신 필요
            if time.time() >= (expiry - 300):
                self.logger.info("저장된 토큰이 만료되었습니다")
                return False

            self.access_token = token_data.get('access_token')
            self.token_expiry = expiry
            self.is_connected = True
            remaining_hours = (expiry - time.time()) / 3600
            self.logger.info(f"✅ 저장된 토큰 로드 성공 (유효시간: {remaining_hours:.1f}시간)")
            return True

        except Exception as e:
            self.logger.warning(f"토큰 로드 실패: {e}")
            return False

    def _save_token(self):
        """토큰을 파일에 저장"""
        try:
            token_data = {
                'access_token': self.access_token,
                'expiry': self.token_expiry,
                'app_key': self.app_key,
                'created_at': time.time()
            }

            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)

            self.logger.info(f"✅ 토큰 저장 완료: {self.token_file}")

        except Exception as e:
            self.logger.warning(f"토큰 저장 실패: {e}")

    def connect(self) -> bool:
        """API 연결 - OAuth 토큰 발급 (저장된 토큰 재사용)"""
        try:
            self.logger.info(f"🔌 API 연결 시작 (거래 모드: {'모의투자' if self.is_simulation else '실전투자'})")
            self.logger.info(f"   서버: {self.base_url}")
            self.logger.info(f"   계좌: {self.account_prefix}-{self.account_suffix}")

            # 먼저 저장된 토큰 로드 시도
            if self._load_token():
                return True

            # 저장된 토큰이 없거나 만료된 경우 새로 발급
            self.logger.info("새로운 API 토큰 발급 요청")
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
                expires_in = result.get('expires_in', 86400)
                self.token_expiry = time.time() + expires_in
                self.is_connected = True

                # 토큰 저장
                self._save_token()

                hours = expires_in / 3600
                self.logger.info(f"✅ 한국투자증권 API 연결 성공 (유효시간: {hours:.1f}시간)")
                return True
            else:
                self.logger.error(f"❌ API 연결 실패: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ API 연결 중 오류 발생: {e}")
            return False

    def disconnect(self):
        """API 연결 해제"""
        self.access_token = None
        self.token_expiry = None
        self.is_connected = False

    def _check_token(self):
        """토큰 유효성 확인 및 갱신"""
        if not self.access_token or (self.token_expiry and time.time() > self.token_expiry - 300):
            self.logger.info("토큰 갱신 필요")
            self.connect()

    def _get_headers(self, tr_id: str) -> Dict:
        """API 요청 헤더 생성"""
        self._check_token()

        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id
        }

    def _call_api(
        self,
        method: str,
        url: str,
        headers: Dict,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
        max_retries: int = 3,
        timeout: int = 10
    ) -> Optional[Dict]:
        """
        공통 API 호출 메서드 (Rate Limiting + 재시도 로직)

        Args:
            method: HTTP 메서드 ('GET' 또는 'POST')
            url: API URL
            headers: 요청 헤더
            params: GET 파라미터
            json_body: POST body (JSON)
            max_retries: 최대 재시도 횟수
            timeout: 요청 타임아웃 (초)

        Returns:
            API 응답 JSON (성공 시) 또는 None (실패 시)
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # Rate Limit 대기
                self._rate_limiter.wait()

                # 재시도 시 추가 대기 (지수 백오프)
                if attempt > 0:
                    backoff_time = min(2 ** attempt, 8)  # 2초, 4초, 8초 (최대 8초)
                    self.logger.info(f"🔄 API 재시도 {attempt}/{max_retries} - {backoff_time}초 대기")
                    time.sleep(backoff_time)

                # API 호출
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=params, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, json=json_body, timeout=timeout)

                # HTTP 오류 처리
                if response.status_code != 200:
                    error_text = response.text
                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error(response.status_code, error_text):
                        self.logger.warning(f"⚠️ Rate Limit 오류 (시도 {attempt + 1}/{max_retries})")
                        last_error = f"Rate Limit: {error_text}"
                        continue
                    # 다른 HTTP 오류
                    self.logger.error(f"HTTP 오류 {response.status_code}: {error_text[:200]}")
                    return None

                # JSON 파싱
                data = response.json()

                # API 레벨 오류 확인
                if data.get('rt_cd') != '0':
                    error_msg = data.get('msg1', '')
                    msg_cd = data.get('msg_cd', '')

                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error_code(msg_cd, error_msg):
                        self.logger.warning(f"⚠️ Rate Limit 오류 (시도 {attempt + 1}/{max_retries}): {error_msg}")
                        last_error = f"Rate Limit: {error_msg}"
                        continue

                    # 다른 API 오류
                    self.logger.error(f"API 오류 (rt_cd={data.get('rt_cd')}): {error_msg}")
                    return None

                # 성공
                return data

            except requests.exceptions.Timeout:
                self.logger.warning(f"⚠️ 요청 타임아웃 (시도 {attempt + 1}/{max_retries})")
                last_error = "Timeout"
                continue
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"⚠️ 네트워크 오류 (시도 {attempt + 1}/{max_retries}): {e}")
                last_error = str(e)
                continue
            except Exception as e:
                self.logger.error(f"❌ 예상치 못한 오류: {e}")
                return None

        # 모든 재시도 실패
        self.logger.error(f"❌ API 호출 실패 (최대 재시도 초과): {last_error}")
        return None

    def _is_rate_limit_error(self, status_code: int, error_text: str) -> bool:
        """HTTP 응답에서 Rate Limit 오류 여부 확인"""
        if status_code == 500 and "EGW00201" in error_text:
            return True
        if "초당 거래건수" in error_text:
            return True
        return False

    def _is_rate_limit_error_code(self, msg_cd: str, msg: str) -> bool:
        """API 응답에서 Rate Limit 오류 코드 확인"""
        if msg_cd == "EGW00201":
            return True
        if "초당 거래건수" in msg:
            return True
        return False

    def get_top_volume_stocks(self, count: int = 30) -> pd.DataFrame:
        """
        거래대금 상위 종목 조회 (개별 종목 조회 방식)

        모의투자 계정에서는 순위 API가 지원되지 않으므로,
        주요 종목 리스트를 개별 조회한 후 거래대금 기준으로 정렬합니다.
        """
        try:
            if not self.stock_list:
                self.logger.error("종목 리스트가 비어있습니다")
                return pd.DataFrame()

            # Rate Limit을 고려하여 처음 50개만 조회 (top 30 선택에 충분)
            query_limit = min(50, len(self.stock_list))
            self.logger.info(f"주요 {query_limit}개 종목 개별 조회 시작...")

            stocks = []
            success_count = 0
            fail_count = 0

            # 주요 종목들을 개별 조회
            for stock_info in self.stock_list[:query_limit]:
                try:
                    stock_code = stock_info['code']
                    stock_name = stock_info['name']

                    # 개별 종목 현재가 조회
                    price_data = self.get_stock_price(stock_code)

                    if price_data and price_data.get('price', 0) > 0:
                        # 거래대금 = 현재가 × 거래량
                        volume = price_data.get('volume', 0)
                        price = price_data.get('price', 0)
                        amount = price * volume

                        stocks.append({
                            'code': stock_code,
                            'name': stock_name,
                            'price': price,
                            'open': price_data.get('open', 0),
                            'high': price_data.get('high', 0),
                            'low': price_data.get('low', 0),
                            'close': price,
                            'volume': volume,
                            'amount': amount,
                            'change_rate': price_data.get('change_rate', 0),
                            'prev_high': price_data.get('high', 0),
                            'prev_low': price_data.get('low', 0)
                        })
                        success_count += 1
                    else:
                        fail_count += 1

                    # Rate limiting은 get_stock_price() 내부에서 처리됨

                except Exception as e:
                    self.logger.debug(f"종목 {stock_code} 조회 실패: {e}")
                    fail_count += 1
                    continue

            if not stocks:
                self.logger.warning(f"조회 성공한 종목이 없습니다 (실패: {fail_count}개)")
                return pd.DataFrame()

            # DataFrame 생성 및 거래대금 기준 내림차순 정렬
            df = pd.DataFrame(stocks)
            df = df.sort_values('amount', ascending=False)

            # 상위 count개만 선택
            df = df.head(count)

            self.logger.info(f"✅ 거래대금 상위 {len(df)}개 종목 조회 완료 (성공: {success_count}, 실패: {fail_count})")
            self.logger.info(f"   1위: {df.iloc[0]['name']} (거래대금: {df.iloc[0]['amount']:,}원)")

            return df

        except Exception as e:
            self.logger.error(f"거래대금 순위 조회 중 오류: {e}")
            return pd.DataFrame()

    def get_stock_price(self, stock_code: str) -> Dict:
        """개별 종목 현재가 조회 (Rate Limiting 적용)"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = self._get_headers("FHKST01010100")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        data = self._call_api('GET', url, headers, params=params)

        if not data:
            return {}

        output = data.get('output', {})

        return {
            'code': stock_code,
            'price': int(output.get('stck_prpr', 0)),
            'open': int(output.get('stck_oprc', 0)),
            'high': int(output.get('stck_hgpr', 0)),
            'low': int(output.get('stck_lwpr', 0)),
            'volume': int(output.get('acml_vol', 0)),
            'change_rate': float(output.get('prdy_ctrt', 0))
        }

    def get_historical_data(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """과거 가격 데이터 조회 (Rate Limiting 적용)"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        headers = self._get_headers("FHKST01010400")

        # 종료일자 (오늘)
        end_date = datetime.now().strftime('%Y%m%d')

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "D",  # D: 일, W: 주, M: 월
            "FID_ORG_ADJ_PRC": "0",  # 0: 수정주가, 1: 원주가
            "FID_INPUT_DATE_1": end_date
        }

        data = self._call_api('GET', url, headers, params=params)

        if not data:
            return pd.DataFrame()

        output = data.get('output', [])

        if not output:
            return pd.DataFrame()

        # 데이터 파싱
        history = []
        for item in output[:days]:
            try:
                date_str = item.get('stck_bsop_date', '')
                date = pd.to_datetime(date_str, format='%Y%m%d')

                history.append({
                    'date': date,
                    'open': int(item.get('stck_oprc', 0)),
                    'high': int(item.get('stck_hgpr', 0)),
                    'low': int(item.get('stck_lwpr', 0)),
                    'close': int(item.get('stck_clpr', 0)),
                    'volume': int(item.get('acml_vol', 0))
                })
            except (ValueError, TypeError):
                continue

        df = pd.DataFrame(history)

        if not df.empty:
            df = df.sort_values('date').set_index('date')

        return df

    def get_minute_data(self, stock_code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 조회"""
        # 한국투자증권 API는 분봉 조회를 별도로 제공하지 않을 수 있음
        # 필요시 실시간 체결가를 사용하거나 일봉 데이터 활용
        self.logger.warning("분봉 데이터는 현재 구현되지 않았습니다")
        return pd.DataFrame()

    def get_order_book(self, stock_code: str) -> Dict:
        """호가창 데이터 조회 (Rate Limiting 적용)"""
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        headers = self._get_headers("FHKST01010200")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        data = self._call_api('GET', url, headers, params=params)

        if not data:
            return {}

        output = data.get('output', {})

        # 호가 데이터 파싱
        bid_prices = []
        ask_prices = []
        bid_volumes = []
        ask_volumes = []

        for i in range(1, 11):  # 10호가
            bid_prices.append(int(output.get(f'bidp{i}', 0)))
            ask_prices.append(int(output.get(f'askp{i}', 0)))
            bid_volumes.append(int(output.get(f'bidp_rsqn{i}', 0)))
            ask_volumes.append(int(output.get(f'askp_rsqn{i}', 0)))

        return {
            'bid': bid_prices,
            'ask': ask_prices,
            'bid_volume': bid_volumes,
            'ask_volume': ask_volumes
        }

    def place_buy_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        매수 주문 (Rate Limit 재시도 로직 포함)

        Args:
            stock_code: 종목 코드
            quantity: 주문 수량
            price: 주문 가격 (None이면 시장가)
            max_retries: 최대 재시도 횟수
        """
        for attempt in range(max_retries):
            try:
                # Rate Limiter를 통한 대기
                self._rate_limiter.wait()

                # 재시도 시 추가 대기 (지수 백오프)
                if attempt > 0:
                    backoff_time = min(2 ** attempt, 8)  # 2초, 4초, 최대 8초
                    self.logger.info(f"🔄 매수 주문 재시도 {attempt}/{max_retries} - {backoff_time}초 대기")
                    time.sleep(backoff_time)

                url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"

                # 모의투자/실전투자에 따라 TR_ID 선택
                tr_id = "VTTC0802U" if self.is_simulation else "TTTC0802U"

                headers = self._get_headers(tr_id)

                body = {
                    "CANO": self.account_prefix,
                    "ACNT_PRDT_CD": self.account_suffix,
                    "PDNO": stock_code,
                    "ORD_DVSN": "01" if price else "01",  # 01: 시장가, 00: 지정가
                    "ORD_QTY": str(quantity),
                    "ORD_UNPR": str(int(price)) if price else "0"
                }

                response = requests.post(url, headers=headers, json=body, timeout=10)

                if response.status_code != 200:
                    error_msg = response.text
                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error(response.status_code, error_msg):
                        if attempt < max_retries - 1:
                            self.logger.warning(f"⚠️ Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
                            continue
                    self.logger.error(f"매수 주문 실패: {response.status_code} - {error_msg}")
                    return {'success': False, 'message': error_msg}

                data = response.json()

                if data.get('rt_cd') == '0':
                    self.logger.info(f"✅ 매수 주문 성공: {stock_code} {quantity}주")
                    return {
                        'success': True,
                        'order_no': data.get('output', {}).get('ODNO', ''),
                        'message': data.get('msg1', '')
                    }
                else:
                    error_msg = data.get('msg1', '')
                    msg_cd = data.get('msg_cd', '')
                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error_code(msg_cd, error_msg):
                        if attempt < max_retries - 1:
                            self.logger.warning(f"⚠️ Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
                            continue
                    self.logger.error(f"매수 주문 실패: {error_msg}")
                    return {'success': False, 'message': error_msg}

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"매수 주문 오류 - 재시도 {attempt + 1}/{max_retries}: {e}")
                    continue
                self.logger.error(f"매수 주문 중 오류: {e}")
                return {'success': False, 'message': str(e)}

        return {'success': False, 'message': 'Max retries exceeded'}

    def place_sell_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        매도 주문 (Rate Limit 재시도 로직 포함)

        Args:
            stock_code: 종목 코드
            quantity: 주문 수량
            price: 주문 가격 (None이면 시장가)
            max_retries: 최대 재시도 횟수
        """
        for attempt in range(max_retries):
            try:
                # Rate Limiter를 통한 대기
                self._rate_limiter.wait()

                # 재시도 시 추가 대기 (지수 백오프)
                if attempt > 0:
                    backoff_time = min(2 ** attempt, 8)  # 2초, 4초, 최대 8초
                    self.logger.info(f"🔄 매도 주문 재시도 {attempt}/{max_retries} - {backoff_time}초 대기")
                    time.sleep(backoff_time)

                url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"

                # 모의투자/실전투자에 따라 TR_ID 선택
                tr_id = "VTTC0801U" if self.is_simulation else "TTTC0801U"

                headers = self._get_headers(tr_id)

                body = {
                    "CANO": self.account_prefix,
                    "ACNT_PRDT_CD": self.account_suffix,
                    "PDNO": stock_code,
                    "ORD_DVSN": "01" if price else "01",  # 01: 시장가, 00: 지정가
                    "ORD_QTY": str(quantity),
                    "ORD_UNPR": str(int(price)) if price else "0"
                }

                response = requests.post(url, headers=headers, json=body, timeout=10)

                if response.status_code != 200:
                    error_msg = response.text
                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error(response.status_code, error_msg):
                        if attempt < max_retries - 1:
                            self.logger.warning(f"⚠️ Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
                            continue
                    self.logger.error(f"매도 주문 실패: {response.status_code} - {error_msg}")
                    return {'success': False, 'message': error_msg}

                data = response.json()

                if data.get('rt_cd') == '0':
                    self.logger.info(f"✅ 매도 주문 성공: {stock_code} {quantity}주")
                    return {
                        'success': True,
                        'order_no': data.get('output', {}).get('ODNO', ''),
                        'message': data.get('msg1', '')
                    }
                else:
                    error_msg = data.get('msg1', '')
                    msg_cd = data.get('msg_cd', '')
                    # Rate Limit 오류 확인
                    if self._is_rate_limit_error_code(msg_cd, error_msg):
                        if attempt < max_retries - 1:
                            self.logger.warning(f"⚠️ Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
                            continue
                    self.logger.error(f"매도 주문 실패: {error_msg}")
                    return {'success': False, 'message': error_msg}

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"매도 주문 오류 - 재시도 {attempt + 1}/{max_retries}: {e}")
                    continue
                self.logger.error(f"매도 주문 중 오류: {e}")
                return {'success': False, 'message': str(e)}

        return {'success': False, 'message': 'Max retries exceeded'}

    def get_account_balance(self) -> Dict:
        """
        계좌 잔고 조회 (Rate Limiting 적용)

        Returns:
            계좌 잔고 정보
            {
                'total_amount': 예수금총액 (현금),
                'available_amount': 주문가능현금,
                'stock_eval_amount': 유가증권평가금액,
                'total_assets': 총평가금액 (순자산),
                'purchase_amount': 매입금액합계,
                'profit_loss': 평가손익합계,
                'next_day_settlement': 익일정산금액 (미수금)
            }
        """
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"

        # 모의투자/실전투자에 따라 TR_ID 선택
        tr_id = "VTTC8434R" if self.is_simulation else "TTTC8434R"

        self.logger.info(f"💰 계좌 잔고 조회 시작 (모드: {'모의투자' if self.is_simulation else '실전투자'})")

        headers = self._get_headers(tr_id)
        params = {
            "CANO": self.account_prefix,
            "ACNT_PRDT_CD": self.account_suffix,
            "AFHR_FLPR_YN": "N",  # 시간외단일가여부
            "OFL_YN": "",  # 오프라인여부
            "INQR_DVSN": "01",  # 조회구분 (01: 대출일별, 02: 종목별)
            "UNPR_DVSN": "01",  # 단가구분
            "FUND_STTL_ICLD_YN": "N",  # 펀드결제분포함여부
            "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액자동상환여부
            "PRCS_DVSN": "00",  # 처리구분 (00: 전일매매포함, 01: 전일매매미포함)
            "CTX_AREA_FK100": "",  # 연속조회검색조건100
            "CTX_AREA_NK100": ""  # 연속조회키100
        }

        data = self._call_api('GET', url, headers, params=params)

        if not data:
            self.logger.error("❌ 잔고 조회 실패")
            return {}

        # output2에 계좌 종합 정보 있음
        output2 = data.get('output2', [{}])[0] if data.get('output2') else {}

        if not output2:
            self.logger.warning("⚠️ 잔고 조회 결과가 비어있습니다 (output2 없음)")
            return {}

        # 정확한 잔고 정보 반환
        balance_info = {
            'total_amount': int(output2.get('dnca_tot_amt', 0)),  # 예수금총액
            'available_amount': int(output2.get('ord_psbl_cash', 0)),  # 주문가능현금
            'stock_eval_amount': int(output2.get('scts_evlu_amt', 0)),  # 유가증권평가금액
            'total_assets': int(output2.get('tot_evlu_amt', 0)),  # 총평가금액 (순자산)
            'net_assets': int(output2.get('nass_amt', 0)),  # 순자산금액
            'purchase_amount': int(output2.get('pchs_amt_smtl_amt', 0)),  # 매입금액합계
            'profit_loss': int(output2.get('evlu_pfls_smtl_amt', 0)),  # 평가손익합계
            'next_day_settlement': int(output2.get('nxdy_excc_amt', 0))  # 익일정산금액 (미수금)
        }

        self.logger.info(
            f"✅ 잔고 조회 성공 - "
            f"주문가능: {balance_info['available_amount']:,}원, "
            f"총자산: {balance_info['total_assets']:,}원, "
            f"보유주식: {balance_info['stock_eval_amount']:,}원"
        )

        return balance_info

    def get_positions(self) -> Optional[List[Dict]]:
        """
        보유 종목 조회 (Rate Limiting 적용)

        Returns:
            보유 종목 리스트 (성공 시)
            빈 리스트 [] (성공했지만 보유 종목 없음)
            None (API 호출 실패)
        """
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"

        # 모의투자/실전투자에 따라 TR_ID 선택
        tr_id = "VTTC8434R" if self.is_simulation else "TTTC8434R"

        self.logger.info(f"📋 보유 종목 조회 시작 (모드: {'모의투자' if self.is_simulation else '실전투자'})")

        headers = self._get_headers(tr_id)
        params = {
            "CANO": self.account_prefix,
            "ACNT_PRDT_CD": self.account_suffix,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }

        data = self._call_api('GET', url, headers, params=params)

        if not data:
            self.logger.error("❌ 보유 종목 조회 실패")
            return None  # API 실패 시 None 반환

        output1 = data.get('output1', [])

        self.logger.info(f"📦 API 응답 - output1 항목 수: {len(output1)}")

        if not output1:
            self.logger.info("ℹ️  보유 종목이 없습니다 (output1 비어있음)")
            return []  # 성공했지만 잔고 없음

        positions = []
        for idx, item in enumerate(output1):
            try:
                quantity = int(item.get('hldg_qty', 0))

                # 디버깅용 로그
                if idx == 0:
                    self.logger.debug(f"첫 번째 항목 원본 데이터: {item}")

                if quantity > 0:
                    position = {
                        'code': item.get('pdno', ''),
                        'name': item.get('prdt_name', ''),
                        'quantity': quantity,
                        'avg_price': float(item.get('pchs_avg_pric', 0)),
                        'current_price': float(item.get('prpr', 0)),
                        'eval_amount': int(item.get('evlu_amt', 0)),
                        'profit_loss': int(item.get('evlu_pfls_amt', 0)),
                        'profit_rate': float(item.get('evlu_pfls_rt', 0))
                    }
                    positions.append(position)

                    self.logger.info(
                        f"  ✓ {position['name']} ({position['code']}): "
                        f"{position['quantity']}주, "
                        f"평균단가 {position['avg_price']:,.0f}원, "
                        f"현재가 {position['current_price']:,.0f}원, "
                        f"손익 {position['profit_loss']:,}원 ({position['profit_rate']:.2f}%)"
                    )
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️ 종목 파싱 실패 (항목 {idx}): {e}")
                continue

        self.logger.info(f"✅ 보유 종목 조회 완료 - 총 {len(positions)}개")
        return positions


# API 팩토리 함수
def create_broker_api(broker_type: str, config: Dict) -> BrokerAPI:
    """
    증권사 API 인스턴스 생성

    Args:
        broker_type: 증권사 타입 ('koreainvestment', 'kiwoom', 'ebest')
        config: API 설정

    Returns:
        BrokerAPI 인스턴스
    """
    if broker_type == 'koreainvestment':
        return KoreaInvestmentAPI(config)
    else:
        raise ValueError(f"지원하지 않는 증권사입니다: {broker_type}")


# 사용 예시
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    config = {
        'app_key': os.getenv('SIMULATION_APP_KEY'),
        'app_secret': os.getenv('SIMULATION_APP_SECRET'),
        'account_number': os.getenv('SIMULATION_ACCOUNT_NUMBER')
    }

    api = create_broker_api('koreainvestment', config)

    if api.connect():
        print("✅ API 연결 성공")

        # 거래대금 상위 종목 조회
        stocks = api.get_top_volume_stocks(10)
        print(f"\n📊 거래대금 상위 10개 종목:")
        print(stocks)

        # 계좌 잔고 조회
        balance = api.get_account_balance()
        print(f"\n💰 계좌 잔고: {balance}")

        # 보유 종목 조회
        positions = api.get_positions()
        print(f"\n📈 보유 종목: {len(positions)}개")
        for pos in positions:
            print(f"  - {pos['name']}: {pos['quantity']}주, 손익률 {pos['profit_rate']}%")
    else:
        print("❌ API 연결 실패")
