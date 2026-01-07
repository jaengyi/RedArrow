"""
증권사 API 연동 모듈

실제 증권사 API를 연동하여 데이터를 수집하고 주문을 체결합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import requests
import hashlib
import time
import json
import os
from datetime import datetime
from pathlib import Path
import logging


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
        # 모의투자 계정(5로 시작)은 모의투자 서버 사용
        self.app_key = config.get('app_key')
        self.app_secret = config.get('app_secret')
        self.account_number = config.get('account_number', '').replace('-', '')

        # 계좌번호로 모의투자 여부 판단
        is_simulation = self.account_number.startswith('5')
        default_url = 'https://openapivts.koreainvestment.com:29443' if is_simulation else 'https://openapi.koreainvestment.com:9443'
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

            self.logger.info(f"주요 {len(self.stock_list)}개 종목 개별 조회 시작...")

            stocks = []
            success_count = 0
            fail_count = 0

            # 주요 종목들을 개별 조회
            for stock_info in self.stock_list:
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

                    # API rate limit 방지를 위해 지연 (초당 요청 제한)
                    time.sleep(0.15)

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
        """개별 종목 현재가 조회"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"

            headers = self._get_headers("FHKST01010100")
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": stock_code
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                self.logger.error(f"현재가 조회 HTTP 오류: {response.status_code} - {response.text}")
                return {}

            data = response.json()

            if data.get('rt_cd') != '0':
                self.logger.error(f"현재가 조회 API 오류: rt_cd={data.get('rt_cd')}, msg={data.get('msg1', '')}")
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

        except Exception as e:
            self.logger.error(f"현재가 조회 중 오류: {e}")
            return {}

    def get_historical_data(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """과거 가격 데이터 조회"""
        try:
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

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                return pd.DataFrame()

            data = response.json()

            if data.get('rt_cd') != '0':
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

        except Exception as e:
            self.logger.error(f"과거 데이터 조회 중 오류: {e}")
            return pd.DataFrame()

    def get_minute_data(self, stock_code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 조회"""
        # 한국투자증권 API는 분봉 조회를 별도로 제공하지 않을 수 있음
        # 필요시 실시간 체결가를 사용하거나 일봉 데이터 활용
        self.logger.warning("분봉 데이터는 현재 구현되지 않았습니다")
        return pd.DataFrame()

    def get_order_book(self, stock_code: str) -> Dict:
        """호가창 데이터 조회"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"

            headers = self._get_headers("FHKST01010200")
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": stock_code
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                return {}

            data = response.json()

            if data.get('rt_cd') != '0':
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

        except Exception as e:
            self.logger.error(f"호가 조회 중 오류: {e}")
            return {}

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
                # API rate limit 방지를 위한 대기
                if attempt > 0:
                    wait_time = 2 ** attempt  # 지수 백오프: 2초, 4초, 8초...
                    self.logger.info(f"재시도 대기 중... ({wait_time}초)")
                    time.sleep(wait_time)
                else:
                    # 첫 시도 전에도 약간 대기 (이전 API 호출과 간격 확보)
                    time.sleep(0.5)

                url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"

                # 모의투자/실전투자 구분
                tr_id = "VTTC0802U" if 'simulation' in self.base_url.lower() or self.account_prefix.startswith('5') else "TTTC0802U"

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
                    if "EGW00201" in error_msg or "초당 거래건수" in error_msg:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
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
                    # Rate Limit 오류 확인
                    if data.get('msg_cd') == 'EGW00201' or "초당 거래건수" in error_msg:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
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
                # API rate limit 방지를 위한 대기
                if attempt > 0:
                    wait_time = 2 ** attempt  # 지수 백오프: 2초, 4초, 8초...
                    self.logger.info(f"재시도 대기 중... ({wait_time}초)")
                    time.sleep(wait_time)
                else:
                    # 첫 시도 전에도 약간 대기 (이전 API 호출과 간격 확보)
                    time.sleep(0.5)

                url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"

                # 모의투자/실전투자 구분
                tr_id = "VTTC0801U" if 'simulation' in self.base_url.lower() or self.account_prefix.startswith('5') else "TTTC0801U"

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
                    if "EGW00201" in error_msg or "초당 거래건수" in error_msg:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
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
                    # Rate Limit 오류 확인
                    if data.get('msg_cd') == 'EGW00201' or "초당 거래건수" in error_msg:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Rate Limit 오류 - 재시도 {attempt + 1}/{max_retries}")
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
        """계좌 잔고 조회"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-psbl-order"

            # 모의투자/실전투자 구분
            tr_id = "VTTC8908R" if 'simulation' in self.base_url.lower() or self.account_prefix.startswith('5') else "TTTC8908R"

            headers = self._get_headers(tr_id)
            params = {
                "CANO": self.account_prefix,
                "ACNT_PRDT_CD": self.account_suffix,
                "PDNO": "005930",  # 더미 종목코드
                "ORD_UNPR": "0",
                "ORD_DVSN": "01",
                "CMA_EVLU_AMT_ICLD_YN": "Y",
                "OVRS_ICLD_YN": "N"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                return {}

            data = response.json()

            if data.get('rt_cd') != '0':
                return {}

            output = data.get('output', {})

            return {
                'total_amount': int(output.get('dnca_tot_amt', 0)),  # 예수금 총액
                'available_amount': int(output.get('ord_psbl_cash', 0)),  # 주문 가능 현금
                'stock_eval_amount': int(output.get('scts_evlu_amt', 0))  # 유가증권 평가금액
            }

        except Exception as e:
            self.logger.error(f"잔고 조회 중 오류: {e}")
            return {}

    def get_positions(self) -> List[Dict]:
        """보유 종목 조회"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"

            # 모의투자/실전투자 구분
            tr_id = "VTTC8434R" if 'simulation' in self.base_url.lower() or self.account_prefix.startswith('5') else "TTTC8434R"

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

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

            if data.get('rt_cd') != '0':
                return []

            output = data.get('output1', [])

            positions = []
            for item in output:
                try:
                    quantity = int(item.get('hldg_qty', 0))
                    if quantity > 0:
                        positions.append({
                            'code': item.get('pdno', ''),
                            'name': item.get('prdt_name', ''),
                            'quantity': quantity,
                            'avg_price': int(item.get('pchs_avg_pric', 0)),
                            'current_price': int(item.get('prpr', 0)),
                            'eval_amount': int(item.get('evlu_amt', 0)),
                            'profit_loss': int(item.get('evlu_pfls_amt', 0)),
                            'profit_rate': float(item.get('evlu_pfls_rt', 0))
                        })
                except (ValueError, TypeError):
                    continue

            return positions

        except Exception as e:
            self.logger.error(f"보유 종목 조회 중 오류: {e}")
            return []


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
