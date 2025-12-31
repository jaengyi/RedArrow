"""
증권사 API 연동 모듈

실제 증권사 API를 연동하여 데이터를 수집하고 주문을 체결합니다.

⚠️  주의: 이 파일은 템플릿입니다.
실제 사용하려면 선택한 증권사의 API 문서를 참고하여 구현해야 합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


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

    ⚠️  실제 구현 필요
    공식 문서: https://apiportal.koreainvestment.com/
    """

    def connect(self) -> bool:
        """API 연결"""
        # TODO: 한국투자증권 API 인증 토큰 발급
        # - OAuth2 인증
        # - 토큰 발급 및 저장
        print("⚠️  한국투자증권 API 연결 구현 필요")
        return False

    def disconnect(self):
        """API 연결 해제"""
        pass

    def get_top_volume_stocks(self, count: int = 30) -> pd.DataFrame:
        """거래대금 상위 종목 조회"""
        # TODO: 실제 API 호출 구현
        print("⚠️  거래대금 상위 종목 조회 API 구현 필요")
        return pd.DataFrame()

    def get_stock_price(self, stock_code: str) -> Dict:
        """개별 종목 현재가 조회"""
        # TODO: 실제 API 호출 구현
        return {}

    def get_historical_data(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """과거 가격 데이터 조회"""
        # TODO: 실제 API 호출 구현
        return pd.DataFrame()

    def get_minute_data(self, stock_code: str, interval: int = 1) -> pd.DataFrame:
        """분봉 데이터 조회"""
        # TODO: 실제 API 호출 구현
        return pd.DataFrame()

    def get_order_book(self, stock_code: str) -> Dict:
        """호가창 데이터 조회"""
        # TODO: 실제 API 호출 구현
        return {}

    def place_buy_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """매수 주문"""
        # TODO: 실제 API 호출 구현
        return {}

    def place_sell_order(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """매도 주문"""
        # TODO: 실제 API 호출 구현
        return {}

    def get_account_balance(self) -> Dict:
        """계좌 잔고 조회"""
        # TODO: 실제 API 호출 구현
        return {}

    def get_positions(self) -> List[Dict]:
        """보유 종목 조회"""
        # TODO: 실제 API 호출 구현
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
    print("""
    ⚠️  이 파일은 템플릿입니다.

    실제 사용하려면 다음 단계를 진행하세요:

    1. 증권사 선택 (한국투자증권, 키움증권, 이베스트투자증권 등)
    2. 해당 증권사 API 문서 확인
    3. BrokerAPI 추상 클래스를 상속받아 구체 클래스 구현
    4. 각 메서드에 실제 API 호출 로직 작성

    참고 문서:
    - 한국투자증권: https://apiportal.koreainvestment.com/
    - 키움증권: https://www.kiwoom.com/
    """)
