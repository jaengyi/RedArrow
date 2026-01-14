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

from apscheduler.schedulers.background import BackgroundScheduler

# 프로젝트 루트를 Python 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import Settings
from src.indicators import TechnicalIndicators
from src.stock_selector import StockSelector
from src.risk_manager import RiskManager
from src.data_collectors.broker_api import create_broker_api
from src.reporter.report_generator import generate_daily_report


# 로깅 설정
def setup_logging(config: Dict):
    """
    로깅 설정을 적용하거나 재적용합니다.
    이 함수는 여러 번 호출될 수 있도록 설계되었습니다.
    """
    log_dir = Path(config.get('log_dir', 'logs'))
    log_dir.mkdir(exist_ok=True)

    log_level = config.get('level', 'INFO')
    log_file = log_dir / f"redarrow_{datetime.now().strftime('%Y%m%d')}.log"

    # 루트 로거 가져오기
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # 기존 핸들러 모두 제거
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # 새로운 핸들러 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 파일 핸들러
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 스트림 핸들러 (콘솔 출력)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

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

        # Broker API 초기화
        broker_config = {
            'app_key': self.settings.app_key,
            'app_secret': self.settings.app_secret,
            'account_number': self.settings.account_number,
            'trading_mode': self.settings.trading_mode  # 명시적으로 거래 모드 전달
        }

        self.broker_api = create_broker_api('koreainvestment', broker_config)

        # API 연결
        if not self.broker_api.connect():
            self.logger.error("❌ 증권사 API 연결 실패. 프로그램을 종료합니다.")
            sys.exit(1)

        self.logger.info("모든 모듈 초기화 완료")

        # 상태 변수
        self.positions: Dict = {}  # 보유 포지션
        self.daily_pnl: float = 0.0  # 당일 손익
        self.account_balance: float = 10000000  # 계좌 잔고 (초기값, API에서 조회하여 갱신)
        self.end_of_day_liquidation_logged: bool = False  # 장 마감 청산 로직 실행 여부

        # 실제 계좌와 동기화
        self.sync_positions_with_account()

    def sync_positions_with_account(self):
        """
        실제 증권사 계좌의 보유 종목과 동기화

        프로그램 시작 시 실제 계좌에 보유 중인 종목을
        메모리상 positions 딕셔너리에 동기화합니다.
        """
        try:
            self.logger.info("📋 계좌 보유 종목 동기화 시작...")

            # 실제 계좌 잔고 조회
            balance_info = self.broker_api.get_account_balance()
            if balance_info and 'available_amount' in balance_info:
                if balance_info['available_amount'] > 0:
                    self.account_balance = balance_info['available_amount']
                    self.logger.info(f"💰 계좌 잔고: {self.account_balance:,}원")
                else:
                    self.logger.warning(f"⚠️ API 잔고 조회 결과가 0원입니다. 기존 잔고({self.account_balance:,}원) 유지")
            else:
                self.logger.warning(f"⚠️ 계좌 잔고 조회 실패. 기존 잔고({self.account_balance:,}원) 유지")

            # 실제 보유 종목 조회
            api_positions = self.broker_api.get_positions()

            if not api_positions:
                self.logger.info("✅ 계좌에 보유 중인 종목이 없습니다")
                return

            # 메모리 positions 초기화 및 동기화
            self.positions.clear()

            for pos in api_positions:
                stock_code = pos['code']
                stock_name = pos['name']

                self.positions[stock_code] = {
                    'name': stock_name,
                    'entry_price': pos['avg_price'],
                    'quantity': pos['quantity'],
                    'highest_price': pos['current_price'],  # 현재가를 최고가로 초기화
                    'entry_time': datetime.now(),  # 진입 시간은 현재 시간으로 설정
                    'order_no': 'SYNCED'  # 동기화된 포지션 표시
                }

                self.logger.info(
                    f"  - {stock_name} ({stock_code}): "
                    f"{pos['quantity']}주 @ {pos['avg_price']:,}원 "
                    f"(평가손익: {pos['profit_loss']:,}원, {pos['profit_rate']:.2f}%)"
                )

            self.logger.info(f"✅ 총 {len(self.positions)}개 종목 동기화 완료")

        except Exception as e:
            self.logger.error(f"계좌 동기화 중 오류 발생: {e}", exc_info=True)

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

        증권사 API를 사용하여 실제 데이터를 수집합니다.

        Returns:
            시장 데이터 딕셔너리
        """
        self.logger.info("시장 데이터 수집 중...")

        try:
            # 거래대금 상위 종목 조회
            stock_data = self.broker_api.get_top_volume_stocks(
                self.settings.stock_selector_config.get('top_volume_count', 30)
            )

            if stock_data.empty:
                self.logger.warning("조회된 종목이 없습니다")
                return {'stock_data': pd.DataFrame(), 'price_history': {}}

            self.logger.info(f"✅ {len(stock_data)}개 종목 조회 완료")

            # 각 종목의 과거 데이터 수집
            price_history = {}

            for _, row in stock_data.iterrows():
                stock_code = row['code']

                try:
                    # 과거 30일 데이터 조회
                    history = self.broker_api.get_historical_data(stock_code, days=30)

                    if not history.empty:
                        price_history[stock_code] = history
                    else:
                        self.logger.warning(f"{row['name']} ({stock_code}) 과거 데이터 없음")

                    # API 호출 제한 방지를 위한 짧은 대기
                    time_module.sleep(0.1)

                except Exception as e:
                    self.logger.warning(f"{row['name']} ({stock_code}) 과거 데이터 조회 실패: {e}")
                    continue

            self.logger.info(f"✅ {len(price_history)}개 종목 과거 데이터 수집 완료")

            return {
                'stock_data': stock_data,
                'price_history': price_history
            }

        except Exception as e:
            self.logger.error(f"시장 데이터 수집 중 오류: {e}")
            return {'stock_data': pd.DataFrame(), 'price_history': {}}

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
        매매 실행

        증권사 API를 사용하여 실제 주문을 체결합니다.

        Args:
            stock: 종목 정보
        """
        # 포지션 수 확인
        if not self.risk_manager.check_max_positions(len(self.positions)):
            self.logger.warning("최대 포지션 수 도달. 매수 불가")
            return

        # 계좌 잔고 확인
        if self.account_balance <= 0:
            self.logger.error(f"❌ 계좌 잔고가 {self.account_balance:,}원으로 매수 불가능합니다.")
            return

        # 포지션 크기 계산
        position = self.risk_manager.calculate_position_size(
            stock['price'],
            self.account_balance,
            risk_percent=2.0
        )

        # 수량이 0이면 매수 불가
        if position['quantity'] <= 0:
            self.logger.warning(
                f"⚠️ 매수 수량이 0주로 계산되었습니다. "
                f"잔고: {self.account_balance:,}원, 주가: {stock['price']:,}원"
            )
            return

        self.logger.info(
            f"매수 주문 준비: {stock['name']} ({stock['code']}) "
            f"{position['quantity']}주, "
            f"{position['amount']:,}원"
        )

        # 실제 매수 주문 실행
        if self.settings.trading_mode == 'simulation':
            self.logger.info("🎮 시뮬레이션 모드 - 실제 주문 실행")

        result = self.broker_api.place_buy_order(
            stock_code=stock['code'],
            quantity=position['quantity'],
            price=stock['price']  # 지정가 주문
        )

        if result.get('success'):
            self.logger.info(
                f"✅ 매수 주문 접수 성공: {stock['name']} "
                f"{position['quantity']}주 @ {stock['price']:,}원 "
                f"(주문번호: {result.get('order_no', 'N/A')})"
            )

            # --- 매수 체결 확인 로직 강화 ---
            order_filled = False
            confirm_timeout_seconds = 20  # 최대 20초간 확인
            confirm_interval_seconds = 2   # 2초 간격으로 확인

            self.logger.info(f"⏳ 주문 체결 확인 시작 (최대 {confirm_timeout_seconds}초)")
            
            start_time = time_module.time()
            while time_module.time() - start_time < confirm_timeout_seconds:
                api_positions = self.broker_api.get_positions()
                
                # API 호출 에러 시 다음 시도까지 대기
                if not isinstance(api_positions, list):
                    self.logger.warning("체결 확인 중 get_positions() API 호출 실패. 잠시 후 재시도.")
                    time_module.sleep(confirm_interval_seconds)
                    continue

                found_position = next((p for p in api_positions if p.get('code') == stock['code']), None)

                if found_position:
                    # 체결 확인됨 - 실제 체결 정보로 포지션 기록
                    self.positions[stock['code']] = {
                        'name': stock['name'],
                        'entry_price': found_position['avg_price'],
                        'quantity': found_position['quantity'],
                        'highest_price': found_position['current_price'],
                        'entry_time': datetime.now(),
                        'order_no': result.get('order_no', '')
                    }
                    self.logger.info(
                        f"✅ 매수 체결 확인됨: {stock['name']} "
                        f"{found_position['quantity']}주 @ {found_position['avg_price']:,}원"
                    )
                    order_filled = True
                    
                    # 매수 금액만큼 계좌 잔고 차감
                    trade_amount = found_position['quantity'] * found_position['avg_price']
                    self.account_balance -= trade_amount
                    self.logger.info(f"💰 매수 후 계좌 잔고: {self.account_balance:,.0f}원")
                    break # while 루프 탈출
                
                # 아직 체결되지 않음, 잠시 대기 후 재시도
                time_module.sleep(confirm_interval_seconds)

            if not order_filled:
                self.logger.warning(
                    f"⚠️ {confirm_timeout_seconds}초 내 매수 주문 체결 미확인: {stock['name']} "
                    f"(주문번호: {result.get('order_no', 'N/A')})"
                )
        else:
            self.logger.error(
                f"❌ 매수 주문 실패: {stock['name']} - {result.get('message', '알 수 없는 오류')}"
            )

    def monitor_positions(self):
        """
        보유 포지션 모니터링 및 청산 판단
        """
        if not self.positions:
            return

        self.logger.info(f"포지션 모니터링 중... (보유: {len(self.positions)}개)")

        for code, position in list(self.positions.items()):
            try:
                # 실제 현재가 조회
                price_info = self.broker_api.get_stock_price(code)

                # API 호출 속도 제한을 위한 지연 추가
                time_module.sleep(0.2)

                if not price_info or 'price' not in price_info:
                    self.logger.warning(f"{position['name']} 현재가 조회 실패")
                    continue

                current_price = price_info['price']

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
                        f"청산 신호: {position['name']} ({code}) - {should_close['reason']} "
                        f"(손익률: {should_close['pnl_percent']:.2f}%)"
                    )

                    # 실제 매도 주문 실행
                    result = self.broker_api.place_sell_order(
                        stock_code=code,
                        quantity=position['quantity'],
                        price=current_price  # 지정가 주문
                    )

                    if result.get('success'):
                        self.logger.info(
                            f"✅ 매도 주문 체결 성공: {position['name']} "
                            f"{position['quantity']}주 @ {current_price:,}원 "
                            f"(주문번호: {result.get('order_no', 'N/A')})"
                        )

                        # 손익 계산 및 잔고 업데이트
                        sell_amount = position['quantity'] * current_price
                        pnl = sell_amount - (position['quantity'] * position['entry_price'])
                        self.daily_pnl += pnl
                        self.account_balance += sell_amount

                        self.logger.info(f"💰 청산 손익: {pnl:,.0f}원 ({should_close['pnl_percent']:.2f}%)")
                        self.logger.info(f"💰 매도 후 계좌 잔고: {self.account_balance:,.0f}원")

                        # 포지션 제거
                        del self.positions[code]
                    else:
                        self.logger.error(
                            f"❌ 매도 주문 실패: {position['name']} - {result.get('message', '알 수 없는 오류')}"
                        )

            except Exception as e:
                self.logger.error(f"{position['name']} 모니터링 중 오류: {e}")
                continue

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
            try:
                # 실제 현재가 조회
                price_info = self.broker_api.get_stock_price(code)

                if not price_info or 'price' not in price_info:
                    self.logger.warning(f"{position['name']} 현재가 조회 실패 - 진입가로 청산 시도")
                    current_price = position['entry_price']
                else:
                    current_price = price_info['price']

                # 실제 매도 주문 실행
                result = self.broker_api.place_sell_order(
                    stock_code=code,
                    quantity=position['quantity'],
                    price=current_price  # 지정가 주문
                )

                if result.get('success'):
                    self.logger.info(
                        f"✅ 청산 주문 체결 성공: {position['name']} "
                        f"{position['quantity']}주, "
                        f"진입가 {position['entry_price']:,}원, "
                        f"청산가 {current_price:,}원 "
                        f"(주문번호: {result.get('order_no', 'N/A')})"
                    )

                    # 손익 계산 및 잔고 업데이트
                    sell_amount = position['quantity'] * current_price
                    pnl = sell_amount - (position['quantity'] * position['entry_price'])
                    pnl_rate = ((current_price / position['entry_price']) - 1) * 100
                    self.daily_pnl += pnl
                    self.account_balance += sell_amount

                    self.logger.info(f"💰 청산 손익: {pnl:,.0f}원 ({pnl_rate:.2f}%)")
                    self.logger.info(f"💰 매도 후 계좌 잔고: {self.account_balance:,.0f}원")

                    # 포지션 제거
                    del self.positions[code]
                else:
                    self.logger.error(
                        f"❌ 청산 주문 실패: {position['name']} - {result.get('message', '알 수 없는 오류')}"
                    )

            except Exception as e:
                self.logger.error(f"{position['name']} 청산 중 오류: {e}")
                continue

        self.logger.info(f"전량 청산 완료. 당일 총 손익: {self.daily_pnl:,.0f}원")

    def run(self):
        """메인 실행 루프 - 24/7 상시 가동"""
        # --- 스케줄러 설정 ---
        scheduler = BackgroundScheduler(timezone='Asia/Seoul')
        scheduler.add_job(generate_daily_report, 'cron', hour=16, minute=0)
        scheduler.start()
        self.logger.info("📅 일일 리포트 생성 스케줄러 시작 (매일 16:00)")
        # ---------------------

        self.logger.info("🚀 RedArrow 시스템 상시 가동 시작")
        self.logger.info(f"거래 모드: {self.settings.trading_mode}")
        self.logger.info(f"모니터링 주기: 60초")

        last_trade_date = datetime.now().date()  # 현재 날짜로 초기화 (중복 동기화 방지)
        last_sync_time = datetime.now()  # 마지막 동기화 시간

        try:
            while True:
                current_time = datetime.now()
                current_date = current_time.date()

                # 새로운 거래일 시작 시 초기화
                if last_trade_date != current_date:
                    # --- 로깅 설정 재적용 ---
                    self.logger = setup_logging(self.settings.logging_config)
                    self.logger.info("="*60)
                    self.logger.info(f"☀️ 새로운 거래일 시작. 로그 파일을 새로 생성합니다: {current_date}")
                    self.logger.info("="*60)
                    # -------------------------

                    self.daily_pnl = 0.0
                    self.end_of_day_liquidation_logged = False  # 장 마감 로그 플래그 초기화
                    last_trade_date = current_date
                    # 새로운 거래일 시작 시 계좌 동기화
                    self.sync_positions_with_account()
                    last_sync_time = current_time

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

                # 10분마다 계좌 동기화 (실제 보유 종목과 메모리 일치 확인)
                time_since_sync = (current_time - last_sync_time).total_seconds()
                if time_since_sync >= 600:  # 10분 = 600초
                    self.logger.info("🔄 주기적 계좌 동기화 수행")
                    self.sync_positions_with_account()
                    last_sync_time = current_time

                # 계좌 잔고 조회 (매시간 정각에 한 번씩)
                if current_time.minute == 0:
                    balance_info = self.broker_api.get_account_balance()
                    if balance_info and 'available_amount' in balance_info:
                        if balance_info['available_amount'] > 0:
                            self.account_balance = balance_info['available_amount']
                            self.logger.info(f"💰 계좌 잔고 업데이트: {self.account_balance:,}원")
                        else:
                            self.logger.warning(f"⚠️ API 잔고 조회 결과가 0원입니다. 잔고를 업데이트하지 않습니다.")

                # 시장 데이터 수집
                market_data = self.collect_market_data()

                # 종목 선정 및 매수 (15:00 이전에만)
                if current_time.time() < time(15, 0):
                    selected_stocks = self.select_stocks(market_data)

                    if selected_stocks:
                        self.logger.info(f"✅ 선정된 종목: {len(selected_stocks)}개")

                        # 매매 실행
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
                if current_time.time() >= time(15, 20):
                    # 하루에 한 번만 청산 확인 로그를 남김
                    if not self.end_of_day_liquidation_logged:
                        self.logger.info("🔔 15:20 도달 - 장 마감 포지션 청산 로직을 확인합니다.")
                        self.end_of_day_liquidation_logged = True

                    if self.positions:
                        self.logger.info("🔥 보유 포지션 확인됨. 전량 청산을 시작합니다.")
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
