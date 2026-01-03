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
import numpy as np
import time as time_module

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

        # 예시: 과거 가격 데이터 (현실적인 추세 포함)
        price_history = {}
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')

        # 삼성전자 - 상승 추세 + 골든크로스 + 거래량 급증
        base_price = 65000
        prices = []
        volumes = []
        for i in range(30):
            # 초반 하락 후 상승 추세
            if i < 10:
                price = base_price + i * 200 + np.random.randint(-500, 500)
            elif i < 20:
                price = base_price + 2000 + (i-10) * 300 + np.random.randint(-500, 500)
            else:
                price = base_price + 5000 + (i-20) * 400 + np.random.randint(-500, 500)

            prices.append(price)

            # 최근 거래량 급증
            if i < 25:
                volume = 8000000 + np.random.randint(-1000000, 1000000)
            else:
                volume = 18000000 + np.random.randint(-2000000, 2000000)  # 2배 이상 급증
            volumes.append(volume)

        price_history['005930'] = pd.DataFrame({
            'open': [p * 0.99 for p in prices],
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': volumes
        }, index=dates)

        # SK하이닉스 - 약한 신호
        base_price = 115000
        prices = [base_price + i * 100 + np.random.randint(-1000, 1000) for i in range(30)]
        volumes = [4500000 + np.random.randint(-500000, 500000) for _ in range(30)]

        price_history['000660'] = pd.DataFrame({
            'open': [p * 0.99 for p in prices],
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': volumes
        }, index=dates)

        # LG화학 - 강한 매수 신호
        base_price = 380000
        prices = []
        volumes = []
        for i in range(30):
            # 큰 상승 추세
            if i < 15:
                price = base_price + i * 500 + np.random.randint(-1000, 1000)
            else:
                price = base_price + 7500 + (i-15) * 800 + np.random.randint(-1000, 1000)

            prices.append(price)

            # 거래량 급증
            if i < 27:
                volume = 1500000 + np.random.randint(-200000, 200000)
            else:
                volume = 4000000 + np.random.randint(-300000, 300000)  # 2.5배 급증
            volumes.append(volume)

        price_history['051910'] = pd.DataFrame({
            'open': [p * 0.99 for p in prices],
            'high': [p * 1.03 for p in prices],
            'low': [p * 0.97 for p in prices],
            'close': prices,
            'volume': volumes
        }, index=dates)

        # 예시: 현재 종목 데이터 (과거 데이터의 최신 값 사용)
        stock_data = pd.DataFrame({
            'code': ['005930', '000660', '051910'],
            'name': ['삼성전자', 'SK하이닉스', 'LG화학'],
            'price': [
                price_history['005930']['close'].iloc[-1],
                price_history['000660']['close'].iloc[-1],
                price_history['051910']['close'].iloc[-1]
            ],
            'open': [
                price_history['005930']['open'].iloc[-1],
                price_history['000660']['open'].iloc[-1],
                price_history['051910']['open'].iloc[-1]
            ],
            'high': [
                price_history['005930']['high'].iloc[-1],
                price_history['000660']['high'].iloc[-1],
                price_history['051910']['high'].iloc[-1]
            ],
            'low': [
                price_history['005930']['low'].iloc[-1],
                price_history['000660']['low'].iloc[-1],
                price_history['051910']['low'].iloc[-1]
            ],
            'close': [
                price_history['005930']['close'].iloc[-1],
                price_history['000660']['close'].iloc[-1],
                price_history['051910']['close'].iloc[-1]
            ],
            'volume': [
                price_history['005930']['volume'].iloc[-1],
                price_history['000660']['volume'].iloc[-1],
                price_history['051910']['volume'].iloc[-1]
            ],
            'amount': [
                price_history['005930']['close'].iloc[-1] * price_history['005930']['volume'].iloc[-1],
                price_history['000660']['close'].iloc[-1] * price_history['000660']['volume'].iloc[-1],
                price_history['051910']['close'].iloc[-1] * price_history['051910']['volume'].iloc[-1]
            ],
            'change_rate': [2.5, 0.8, 3.1],
            'prev_high': [
                price_history['005930']['high'].iloc[-2],
                price_history['000660']['high'].iloc[-2],
                price_history['051910']['high'].iloc[-2]
            ],
            'prev_low': [
                price_history['005930']['low'].iloc[-2],
                price_history['000660']['low'].iloc[-2],
                price_history['051910']['low'].iloc[-2]
            ]
        })

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

    def close_all_positions(self):
        """
        모든 포지션 청산 (장 마감 전 청산)
        """
        if not self.positions:
            return

        self.logger.info(f"전량 청산 시작 (보유 포지션: {len(self.positions)}개)")

        for code, position in list(self.positions.items()):
            # TODO: 실제 현재가 조회
            current_price = position['entry_price'] * 1.01  # 예시

            # TODO: 실제 매도 주문 실행
            self.logger.info(
                f"청산 주문: {position['name']} "
                f"{position['quantity']}주, "
                f"진입가 {position['entry_price']:,}원, "
                f"현재가 {current_price:,}원"
            )

            # 손익 계산
            pnl = position['quantity'] * (current_price - position['entry_price'])
            self.daily_pnl += pnl

            # 포지션 제거
            del self.positions[code]

        self.logger.info(f"전량 청산 완료. 당일 총 손익: {self.daily_pnl:,.0f}원")

    def run(self):
        """메인 실행 루프 - 24/7 상시 가동"""
        self.logger.info("🚀 RedArrow 시스템 상시 가동 시작")
        self.logger.info(f"거래 모드: {self.settings.trading_mode}")
        self.logger.info(f"모니터링 주기: 60초")

        last_trade_date = None  # 마지막 거래일 추적

        try:
            while True:
                current_time = datetime.now()
                current_date = current_time.date()

                # 새로운 거래일 시작 시 초기화
                if last_trade_date != current_date:
                    if last_trade_date is not None:
                        self.logger.info("="*60)
                        self.logger.info(f"새로운 거래일 시작: {current_date}")
                        self.logger.info("="*60)
                    self.daily_pnl = 0.0
                    last_trade_date = current_date

                # 시장 개장 확인
                if not self.is_market_open():
                    # 장 시작 전/후에는 10분마다 체크
                    if current_time.hour < 9:
                        self.logger.info(f"⏰ 장 시작 전 대기 중... (현재 시각: {current_time.strftime('%H:%M:%S')})")
                    else:
                        self.logger.info(f"🌙 장 마감. 내일 개장까지 대기... (현재 시각: {current_time.strftime('%H:%M:%S')})")

                    time_module.sleep(600)  # 10분 대기
                    continue

                # 일일 손실 제한 확인
                if not self.check_daily_limit():
                    self.logger.info("⛔ 일일 손실 제한 도달. 오늘은 거래를 중단합니다.")
                    time_module.sleep(600)  # 10분 대기
                    continue

                # === 개장 중 메인 루프 ===
                self.logger.info(f"📊 시장 개장 중 - 모니터링 실행 ({current_time.strftime('%H:%M:%S')})")

                # 시장 데이터 수집
                market_data = self.collect_market_data()

                # 종목 선정 및 매수 (15:00 이전에만)
                if current_time.time() < time(15, 0):
                    selected_stocks = self.select_stocks(market_data)

                    if selected_stocks:
                        self.logger.info(f"✅ 선정된 종목: {len(selected_stocks)}개")

                        # 매매 실행
                        if self.settings.trading_mode == 'simulation':
                            self.logger.info("🎮 시뮬레이션 모드: 실제 주문은 실행되지 않습니다.")

                        for stock in selected_stocks[:3]:  # 상위 3개 종목만
                            if self.risk_manager.check_max_positions(len(self.positions)):
                                self.execute_trade(stock)
                    else:
                        self.logger.info("ℹ️  선정된 종목이 없습니다.")

                # 포지션 모니터링 (항상 실행)
                if self.positions:
                    self.monitor_positions()
                    self.logger.info(f"💰 현재 손익: {self.daily_pnl:,.0f}원, 보유 포지션: {len(self.positions)}개")

                # 15:20 이후 전량 청산
                if current_time.time() >= time(15, 20) and self.positions:
                    self.logger.info("🔔 15:20 도달 - 전량 청산을 시작합니다.")
                    self.close_all_positions()

                # 1분 대기
                time_module.sleep(60)

        except KeyboardInterrupt:
            self.logger.info("\n⚠️  사용자에 의해 프로그램이 중단되었습니다.")

            # 남은 포지션이 있으면 경고
            if self.positions:
                self.logger.warning(f"⚠️  미청산 포지션 {len(self.positions)}개가 남아있습니다!")
                for code, pos in self.positions.items():
                    self.logger.warning(f"   - {pos['name']}: {pos['quantity']}주")

        except Exception as e:
            self.logger.error(f"❌ 오류 발생: {e}", exc_info=True)

        finally:
            self.logger.info("="*60)
            self.logger.info("RedArrow 시스템 종료")
            self.logger.info(f"최종 손익: {self.daily_pnl:,.0f}원")
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
