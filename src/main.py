"""
RedArrow 메인 실행 파일

단기투자 종목 선정 시스템의 메인 진입점입니다.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, time
from typing import Dict, List
import pandas as pd

# 프로젝트 루트를 Python 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import Settings
from src.indicators import TechnicalIndicators
from src.stock_selector import StockSelector
from src.risk_manager import RiskManager


# 로깅 설정
def setup_logging(config: Dict):
    """로깅 설정"""
    log_dir = Path(config.get('log_dir', 'logs'))
    log_dir.mkdir(exist_ok=True)

    log_level = config.get('level', 'INFO')
    log_file = log_dir / f"redarrow_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


class RedArrowSystem:
    """RedArrow 메인 시스템 클래스"""

    def __init__(self):
        """초기화"""
        # 설정 로드
        self.settings = Settings()

        # 로깅 설정
        self.logger = setup_logging(self.settings.logging_config)
        self.logger.info("="*60)
        self.logger.info("RedArrow 시스템 시작")
        self.logger.info("="*60)

        # 설정 검증
        if not self.settings.validate():
            self.logger.error("설정 검증 실패. 프로그램을 종료합니다.")
            sys.exit(1)

        # 설정 요약 출력
        self.settings.print_summary()

        # 모듈 초기화
        self.stock_selector = StockSelector(
            self.settings.stock_selector_config
        )
        self.risk_manager = RiskManager(
            self.settings.risk_management_config
        )
        self.indicators = TechnicalIndicators()

        self.logger.info("모든 모듈 초기화 완료")

        # 상태 변수
        self.positions: Dict = {}  # 보유 포지션
        self.daily_pnl: float = 0.0  # 당일 손익
        self.account_balance: float = 10000000  # 계좌 잔고 (예시)

    def is_market_open(self) -> bool:
        """
        시장 개장 시간 확인

        Returns:
            시장 개장 여부
        """
        now = datetime.now().time()
        market_hours = self.settings.market_hours

        open_time = time.fromisoformat(market_hours.get('open_time', '09:00'))
        close_time = time.fromisoformat(market_hours.get('close_time', '15:30'))

        return open_time <= now <= close_time

    def collect_market_data(self) -> Dict:
        """
        시장 데이터 수집

        실제 구현 시 증권사 API를 사용하여 데이터를 수집합니다.

        Returns:
            시장 데이터 딕셔너리
        """
        self.logger.info("시장 데이터 수집 중...")

        # TODO: 실제 증권사 API 연동 필요
        # 현재는 예시 데이터 구조만 반환

        # 예시: 거래대금 상위 종목 데이터
        stock_data = pd.DataFrame({
            'code': ['005930', '000660', '051910'],
            'name': ['삼성전자', 'SK하이닉스', 'LG화학'],
            'price': [70000, 120000, 400000],
            'open': [69000, 119000, 395000],
            'high': [71000, 122000, 405000],
            'low': [68500, 118000, 393000],
            'close': [70000, 120000, 400000],
            'volume': [10000000, 5000000, 2000000],
            'amount': [700000000000, 600000000000, 800000000000],
            'change_rate': [1.5, 0.8, 2.1],
            'prev_high': [70500, 121000, 402000],
            'prev_low': [68000, 117500, 392000]
        })

        # 예시: 과거 가격 데이터
        price_history = {}
        for code in stock_data['code']:
            # 실제로는 과거 30일 데이터를 가져와야 함
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            price_history[code] = pd.DataFrame({
                'open': [70000] * 30,
                'high': [71000] * 30,
                'low': [69000] * 30,
                'close': [70000] * 30,
                'volume': [10000000] * 30
            }, index=dates)

        return {
            'stock_data': stock_data,
            'price_history': price_history
        }

    def select_stocks(self, market_data: Dict) -> List[Dict]:
        """
        종목 선정

        Args:
            market_data: 시장 데이터

        Returns:
            선정된 종목 리스트
        """
        self.logger.info("종목 선정 시작...")

        selected_stocks = self.stock_selector.select_stocks(
            market_data['stock_data'],
            market_data['price_history']
        )

        self.logger.info(f"선정된 종목 수: {len(selected_stocks)}")

        for stock in selected_stocks:
            self.logger.info(
                f"  - {stock['name']} ({stock['code']}): "
                f"점수 {stock['score']}, 가격 {stock['price']:,}원"
            )

        return selected_stocks

    def execute_trade(self, stock: Dict):
        """
        매매 실행 (예시)

        실제 구현 시 증권사 API를 사용하여 주문을 체결합니다.

        Args:
            stock: 종목 정보
        """
        # 포지션 수 확인
        if not self.risk_manager.check_max_positions(len(self.positions)):
            self.logger.warning("최대 포지션 수 도달. 매수 불가")
            return

        # 포지션 크기 계산
        position = self.risk_manager.calculate_position_size(
            stock['price'],
            self.account_balance,
            risk_percent=2.0
        )

        self.logger.info(
            f"매수 주문: {stock['name']} "
            f"{position['quantity']}주, "
            f"{position['amount']:,}원"
        )

        # TODO: 실제 매수 주문 실행

        # 포지션 기록
        self.positions[stock['code']] = {
            'name': stock['name'],
            'entry_price': stock['price'],
            'quantity': position['quantity'],
            'highest_price': stock['price'],
            'entry_time': datetime.now()
        }

    def monitor_positions(self):
        """
        보유 포지션 모니터링 및 청산 판단
        """
        if not self.positions:
            return

        self.logger.info(f"포지션 모니터링 중... (보유: {len(self.positions)}개)")

        for code, position in list(self.positions.items()):
            # TODO: 실제 현재가 조회
            current_price = position['entry_price'] * 1.01  # 예시: 1% 상승

            # 최고가 업데이트
            if current_price > position['highest_price']:
                position['highest_price'] = current_price

            # 청산 여부 판단
            should_close = self.risk_manager.should_close_position(
                entry_price=position['entry_price'],
                current_price=current_price,
                highest_price=position['highest_price'],
                current_time=datetime.now()
            )

            if should_close['should_close']:
                self.logger.info(
                    f"청산 신호: {position['name']} - {should_close['reason']} "
                    f"(손익률: {should_close['pnl_percent']:.2f}%)"
                )

                # TODO: 실제 매도 주문 실행

                # 포지션 제거
                del self.positions[code]

                # 손익 기록
                pnl = position['quantity'] * (current_price - position['entry_price'])
                self.daily_pnl += pnl

    def check_daily_limit(self) -> bool:
        """
        일일 손실 제한 확인

        Returns:
            거래 계속 가능 여부
        """
        result = self.risk_manager.check_daily_loss_limit(
            self.daily_pnl,
            self.account_balance
        )

        if result['limit_reached']:
            self.logger.error(
                f"일일 손실 제한 도달: {result['daily_loss_percent']:.2f}%"
            )
            self.logger.error("모든 거래를 중단합니다.")
            return False

        return True

    def run(self):
        """메인 실행 루프"""
        try:
            # 시장 개장 대기
            if not self.is_market_open():
                self.logger.info("시장이 개장하지 않았습니다. 대기 중...")
                return

            # 일일 손실 제한 확인
            if not self.check_daily_limit():
                return

            # 시장 데이터 수집
            market_data = self.collect_market_data()

            # 종목 선정
            selected_stocks = self.select_stocks(market_data)

            # 매매 실행 (시뮬레이션)
            if self.settings.trading_mode == 'simulation':
                self.logger.info("시뮬레이션 모드: 실제 주문은 실행되지 않습니다.")

                for stock in selected_stocks[:3]:  # 상위 3개 종목만
                    self.execute_trade(stock)

            # 포지션 모니터링
            self.monitor_positions()

            self.logger.info(f"당일 손익: {self.daily_pnl:,.0f}원")

        except KeyboardInterrupt:
            self.logger.info("\n사용자에 의해 프로그램이 중단되었습니다.")
        except Exception as e:
            self.logger.error(f"오류 발생: {e}", exc_info=True)
        finally:
            self.logger.info("="*60)
            self.logger.info("RedArrow 시스템 종료")
            self.logger.info("="*60)


def main():
    """메인 함수"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                  RedArrow Trading System                  ║
    ║                  단기투자 종목 선정 시스템                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    system = RedArrowSystem()
    system.run()


if __name__ == "__main__":
    main()
