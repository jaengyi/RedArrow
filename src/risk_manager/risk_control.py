"""
리스크 관리 모듈

손절매, 익절, 포지션 크기 결정 등 리스크 관리 기능을 제공합니다.

===============================================================================
[학습 가이드] - 이 파일을 읽기 전에
===============================================================================

📚 이 파일의 역할:
    - 투자 손실을 최소화하고 수익을 보호하는 리스크 관리 기능 제공
    - 손절매(Stop-Loss), 익절(Take-Profit), 트레일링 스톱 등 구현
    - 포지션 크기 결정으로 과도한 투자 방지

🎯 학습 목표:
    1. 리스크 관리의 중요성과 핵심 개념 이해하기
    2. 손절/익절/트레일링 스톱의 원리 배우기
    3. 포지션 크기 계산 방법 익히기

📖 사전 지식:
    - 주식 거래의 기본 (매수가, 현재가, 손익률)
    - 기본적인 수학 (퍼센트 계산)

🔗 관련 파일:
    - config/config.yaml: 리스크 관리 설정값
    - src/main.py: 포지션 모니터링에서 이 모듈 사용

💡 리스크 관리가 중요한 이유:
    "손실을 작게, 수익을 크게" - 투자의 황금률

    나쁜 예: 손절 안 함 → -50% 손실 → 원금 회복에 +100% 필요!
    좋은 예: 손절 -2.5% → 원금 회복에 +2.6% 필요 (관리 가능)

    통계적으로 승률이 50%여도 손익비(Risk-Reward Ratio)가
    1:2 이상이면 장기적으로 수익을 낼 수 있습니다.

⚠️ 핵심 원칙:
    1. 손절은 반드시 실행 (예외 없음)
    2. 익절은 유연하게 (추세가 지속되면 보유)
    3. 트레일링 스톱으로 수익 보호

===============================================================================
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime, time


# ============================================================================
# [학습 포인트] 리스크 관리 클래스
# ============================================================================
# 이 클래스는 투자 손실을 제한하고 수익을 보호하는 모든 기능을 담당합니다.
#
# 핵심 메서드:
#   check_stop_loss(): 손절 조건 확인
#   check_take_profit(): 익절 조건 확인
#   calculate_trailing_stop(): 트레일링 스톱 계산
#   calculate_position_size(): 포지션 크기 결정
#   should_close_position(): 청산 여부 종합 판단
# ============================================================================

class RiskManager:
    """리스크 관리 클래스"""

    def __init__(self, config: Dict):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config

        # ====================================================================
        # [학습 포인트] 리스크 관리 설정값
        # ====================================================================
        # 이 값들은 투자 성과에 큰 영향을 미칩니다.
        # 백테스팅을 통해 최적값을 찾는 것이 좋습니다.
        #
        # 각 설정의 의미:
        #   stop_loss_percent: 손절 기준 (매수가 대비 -2.5% → 손절)
        #   take_profit_percent: 익절 기준 (매수가 대비 +5% → 익절)
        #   trailing_stop_percent: 최고가 대비 하락률 (-1.5% → 청산)
        #   max_position_size: 한 종목당 최대 투자금 (100만원)
        #   max_positions: 동시 보유 가능 종목 수 (5개)
        #   daily_loss_limit: 일일 최대 손실률 (-5% → 당일 거래 중단)
        # ====================================================================

        # 손절 설정 - 손실을 제한하는 가장 중요한 설정
        self.stop_loss_percent = config.get('stop_loss_percent', 2.5)

        # 익절 설정 - 목표 수익률 도달 시 이익 실현
        self.take_profit_percent = config.get('take_profit_percent', 5.0)

        # 트레일링 스톱 설정 - 수익 보호 (뒤에서 자세히 설명)
        self.trailing_stop = config.get('trailing_stop', True)
        self.trailing_stop_percent = config.get('trailing_stop_percent', 1.5)

        # 포지션 관리 - 분산 투자와 리스크 제한
        self.max_position_size = config.get('max_position_size', 1000000)  # 종목당 최대 100만원
        self.max_positions = config.get('max_positions', 5)  # 최대 5종목

        # 오버나이트 설정 - 야간 리스크 관리
        self.overnight_hold = config.get('overnight_hold', False)  # 기본: 당일 청산
        self.overnight_min_profit = config.get('overnight_min_profit', 2.0)  # 익절 2% 이상만 보유

        # 일일 손실 제한 - 폭락장 대응
        self.daily_loss_limit = config.get('daily_loss_limit', -5.0)  # -5% 손실 시 거래 중단

        # 종목당 최대 투자 비중 (계좌 총자산 대비)
        self.max_single_stock_ratio = config.get('max_single_stock_ratio', 0.2)  # 20%

    def check_stop_loss(
        self,
        entry_price: float,
        current_price: float,
        ma_value: Optional[float] = None
    ) -> Dict[str, any]:
        """
        손절 기준 확인

        Args:
            entry_price: 매수가
            current_price: 현재가
            ma_value: 이동평균선 값 (선택사항)

        Returns:
            {'should_stop': 손절 여부, 'reason': 손절 사유, 'loss_percent': 손실률}
        """
        # ====================================================================
        # [학습 포인트] 손절매 (Stop-Loss)
        # ====================================================================
        # 손절은 투자에서 가장 중요한 리스크 관리 기법입니다.
        #
        # 왜 손절이 중요한가?
        #   - 손실 10% → 원금 회복에 11% 수익 필요
        #   - 손실 20% → 원금 회복에 25% 수익 필요
        #   - 손실 50% → 원금 회복에 100% 수익 필요!
        #   → 손실이 커질수록 회복이 기하급수적으로 어려워짐
        #
        # 손절 기준 2가지:
        #   1. 퍼센트 기준: 매수가 대비 일정 % 하락 시
        #   2. 기술적 기준: 이동평균선 이탈 시 (추세 전환 신호)
        #
        # 손절 실행의 심리적 어려움:
        #   "조금만 더 기다리면 오를 것 같은데..." (희망적 사고)
        #   → 시스템 매매는 감정을 배제하고 규칙대로 실행
        # ====================================================================

        # 손익률 계산: (현재가 - 매수가) / 매수가 × 100
        loss_percent = ((current_price - entry_price) / entry_price) * 100

        # 1. 퍼센트 기준 손절 (가장 기본적인 방법)
        if loss_percent <= -self.stop_loss_percent:  # -2.5% 이하면 손절
            return {
                'should_stop': True,
                'reason': f'손실률 {self.stop_loss_percent}% 초과',
                'loss_percent': loss_percent
            }

        # 2. 이동평균선 이탈 손절 (기술적 분석 기반)
        # 주가가 이동평균선 아래로 내려가면 상승 추세가 깨진 것으로 판단
        if ma_value is not None and current_price < ma_value:
            return {
                'should_stop': True,
                'reason': '이동평균선 이탈',
                'loss_percent': loss_percent
            }

        return {
            'should_stop': False,
            'reason': None,
            'loss_percent': loss_percent
        }

    def check_take_profit(
        self,
        entry_price: float,
        current_price: float
    ) -> Dict[str, any]:
        """
        익절 기준 확인

        Args:
            entry_price: 매수가
            current_price: 현재가

        Returns:
            {'should_profit': 익절 여부, 'profit_percent': 수익률}
        """
        profit_percent = ((current_price - entry_price) / entry_price) * 100

        if profit_percent >= self.take_profit_percent:
            return {
                'should_profit': True,
                'profit_percent': profit_percent
            }

        return {
            'should_profit': False,
            'profit_percent': profit_percent
        }

    def calculate_trailing_stop(
        self,
        entry_price: float,
        highest_price: float,
        current_price: float
    ) -> Dict[str, any]:
        """
        트레일링 스톱 계산

        Args:
            entry_price: 매수가
            highest_price: 매수 후 최고가
            current_price: 현재가

        Returns:
            {'should_stop': 트레일링 스톱 발동 여부,
             'trailing_stop_price': 트레일링 스톱 가격}
        """
        # ====================================================================
        # [학습 포인트] 트레일링 스톱 (Trailing Stop)
        # ====================================================================
        # 트레일링 스톱은 수익을 보호하면서 상승 추세를 따라가는 기법입니다.
        #
        # 작동 원리:
        #   - 주가가 오르면 청산 기준가도 함께 올라감
        #   - 주가가 내리면 청산 기준가는 그대로 유지
        #   - 주가가 청산 기준가 아래로 내려오면 청산
        #
        # 예시 (trailing_stop_percent = 1.5%):
        #   매수가: 100원
        #   최고가: 110원 → 청산 기준가: 110 × (1 - 0.015) = 108.35원
        #   현재가: 107원 → 107 < 108.35 → 트레일링 스톱 발동!
        #   → 10원 수익 중 7원 확보 (최고점 대비 약간 손실, 원금 대비 이익)
        #
        # 장점:
        #   - 이익을 내면서 청산 (손실로 끝나지 않음)
        #   - 추세가 계속되면 더 큰 수익 가능
        #   - 고점에서 하락 시 자동으로 이익 실현
        #
        # 조건: 현재가 > 매수가 (원금 보존)
        #   → 손실 구간에서는 트레일링 스톱 미적용 (일반 손절 적용)
        # ====================================================================
        if not self.trailing_stop:
            return {'should_stop': False, 'trailing_stop_price': None}

        # 최고가 대비 하락률 계산
        drop_from_high = ((current_price - highest_price) / highest_price) * 100

        # 트레일링 스톱 가격 계산: 최고가 × (1 - 하락률)
        trailing_stop_price = highest_price * (1 - self.trailing_stop_percent / 100)

        # 트레일링 스톱 발동 조건:
        # 1. 현재가가 최고가 대비 일정 % 하락
        # 2. 현재가가 매수가보다는 높아야 함 (손실 방지)
        should_stop = (
            drop_from_high <= -self.trailing_stop_percent and
            current_price > entry_price  # 이익 구간에서만 발동
        )

        return {
            'should_stop': should_stop,
            'trailing_stop_price': trailing_stop_price,
            'drop_from_high': drop_from_high
        }

    def calculate_position_size(
        self,
        stock_price: float,
        account_balance: float,
        risk_percent: float = 2.0
    ) -> Dict[str, any]:
        """
        포지션 크기 계산

        Args:
            stock_price: 주식 가격
            account_balance: 계좌 잔고
            risk_percent: 리스크 비율 (기본 2%)

        Returns:
            {'quantity': 매수 수량, 'amount': 매수 금액, 'risk_amount': 리스크 금액}
        """
        # ====================================================================
        # [학습 포인트] 포지션 사이징 (Position Sizing)
        # ====================================================================
        # 얼마나 많이 살 것인가? - 리스크 관리의 핵심!
        #
        # 원칙: "한 번의 거래로 계좌의 X% 이상 잃지 않는다"
        #
        # 계산 방법:
        #   1. 리스크 금액 = 계좌 잔고 × 리스크 비율 (예: 1000만원 × 2% = 20만원)
        #   2. 손실 시 잃는 금액 = 매수 수량 × 주가 × 손절률
        #   3. 리스크 금액 = 손실 금액이 되도록 수량 계산
        #
        # 예시:
        #   계좌 잔고: 1000만원, 리스크 비율: 2%, 손절률: 2.5%
        #   리스크 금액: 20만원 (한 번 거래로 최대 20만원 손실)
        #   주가: 10000원
        #   최대 수량: 20만원 / (10000원 × 2.5%) = 80주
        #   → 80주 × 10000원 = 80만원 매수
        #   → 손절 시 손실: 80만원 × 2.5% = 2만원 (계좌의 0.2%)
        #
        # 제한:
        #   - max_position_size: 종목당 최대 투자금 (집중 투자 방지)
        #   - 둘 중 작은 값 사용
        # ====================================================================

        # 잔고 또는 주가가 0 이하인 경우 처리
        if account_balance <= 0 or stock_price <= 0:
            return {
                'quantity': 0,
                'amount': 0,
                'risk_amount': 0
            }

        # 리스크 금액 계산 (계좌 잔고의 risk_percent%)
        # 이 금액이 한 번의 거래에서 잃을 수 있는 최대 금액
        risk_amount = account_balance * (risk_percent / 100)

        # 손절가 기준으로 매수 수량 계산
        # 공식: 리스크 금액 = 매수 수량 × 주가 × 손절률
        # 따라서: 매수 수량 = 리스크 금액 / (주가 × 손절률)
        max_quantity = int(
            risk_amount / (stock_price * (self.stop_loss_percent / 100))
        )

        # 최대 포지션 크기 제한 (종목당 투자 한도)
        max_position_quantity = int(self.max_position_size / stock_price)
        quantity = min(max_quantity, max_position_quantity)  # 둘 중 작은 값

        # 실제 매수 금액
        amount = quantity * stock_price

        return {
            'quantity': quantity,  # 매수 수량
            'amount': amount,  # 총 매수 금액
            'risk_amount': risk_amount  # 리스크 금액 (정보용)
        }

    def check_overnight_eligibility(
        self,
        entry_price: float,
        current_price: float,
        market_status: str = 'normal'
    ) -> Dict[str, any]:
        """
        오버나이트 보유 여부 결정

        Args:
            entry_price: 매수가
            current_price: 현재가
            market_status: 시장 상태 ('normal', 'volatile', 'stable')

        Returns:
            {'should_hold': 보유 여부, 'reason': 사유}
        """
        # 오버나이트 설정이 꺼져있으면 무조건 청산
        if not self.overnight_hold:
            return {
                'should_hold': False,
                'reason': '오버나이트 설정 비활성화'
            }

        # 수익률 계산
        profit_percent = ((current_price - entry_price) / entry_price) * 100

        # 최소 수익률 미달 시 청산
        if profit_percent < self.overnight_min_profit:
            return {
                'should_hold': False,
                'reason': f'수익률 {self.overnight_min_profit}% 미달'
            }

        # 시장 상황이 불안정하면 청산
        if market_status == 'volatile':
            return {
                'should_hold': False,
                'reason': '시장 불안정'
            }

        # 조건 충족 시 보유
        return {
            'should_hold': True,
            'reason': f'수익률 {profit_percent:.2f}%, 시장 안정'
        }

    def check_daily_loss_limit(
        self,
        daily_pnl: float,
        account_balance: float
    ) -> Dict[str, any]:
        """
        일일 손실 제한 확인

        Args:
            daily_pnl: 당일 손익 (절대값)
            account_balance: 계좌 잔고

        Returns:
            {'limit_reached': 제한 도달 여부, 'daily_loss_percent': 일일 손실률}
        """
        # 기준 잔고가 초기화되지 않은 경우 (아직 총자산 조회 전)
        if account_balance <= 0:
            return {
                'limit_reached': False,
                'daily_loss_percent': 0.0,
                'message': f'기준 잔고 미설정 (잔고: {account_balance:,.0f}원) - 손실 제한 검사 생략'
            }

        # 일일 손실률 계산
        daily_loss_percent = (daily_pnl / account_balance) * 100

        # 일일 손실 제한 도달 여부
        limit_reached = daily_loss_percent <= self.daily_loss_limit

        return {
            'limit_reached': limit_reached,
            'daily_loss_percent': daily_loss_percent,
            'message': f'일일 손실률: {daily_loss_percent:.2f}%'
        }

    def check_max_positions(
        self,
        current_positions: int
    ) -> bool:
        """
        최대 포지션 수 확인

        Args:
            current_positions: 현재 보유 포지션 수

        Returns:
            추가 매수 가능 여부
        """
        return current_positions < self.max_positions

    def check_stock_concentration(
        self,
        current_invested: float,
        new_order_amount: float,
        total_account_value: float
    ) -> Dict[str, any]:
        """
        종목당 비중 상한 확인

        현재 투자금 + 신규 주문금이 계좌 총자산 대비 max_single_stock_ratio를
        초과하는지 검사합니다. 초과 시 허용 가능한 잔여 금액을 반환합니다.

        Args:
            current_invested: 해당 종목 현재 투자금 (보유수량 * 매입가)
            new_order_amount: 신규 주문 금액
            total_account_value: 계좌 총자산

        Returns:
            {'allowed': 주문 가능 여부,
             'max_amount': 해당 종목 최대 투자 가능 금액,
             'remaining_amount': 추가 투자 가능 잔여 금액,
             'current_ratio': 현재 투자 비중}
        """
        if total_account_value <= 0:
            return {
                'allowed': False,
                'max_amount': 0,
                'remaining_amount': 0,
                'current_ratio': 0.0
            }

        max_amount = total_account_value * self.max_single_stock_ratio
        current_ratio = current_invested / total_account_value if total_account_value > 0 else 0.0
        remaining_amount = max(0, max_amount - current_invested)
        total_after_order = current_invested + new_order_amount

        return {
            'allowed': total_after_order <= max_amount,
            'max_amount': max_amount,
            'remaining_amount': remaining_amount,
            'current_ratio': current_ratio
        }

    def should_close_position(
        self,
        entry_price: float,
        current_price: float,
        highest_price: float,
        ma_value: Optional[float] = None,
        current_time: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        포지션 청산 여부 종합 판단

        Args:
            entry_price: 매수가
            current_price: 현재가
            highest_price: 매수 후 최고가
            ma_value: 이동평균선 값
            current_time: 현재 시간

        Returns:
            {'should_close': 청산 여부, 'reason': 청산 사유, 'pnl_percent': 손익률}
        """
        # 1. 손절 확인
        stop_loss_result = self.check_stop_loss(entry_price, current_price, ma_value)
        if stop_loss_result['should_stop']:
            return {
                'should_close': True,
                'reason': f"손절: {stop_loss_result['reason']}",
                'pnl_percent': stop_loss_result['loss_percent']
            }

        # 2. 익절 확인
        take_profit_result = self.check_take_profit(entry_price, current_price)
        if take_profit_result['should_profit']:
            return {
                'should_close': True,
                'reason': '목표 수익률 달성',
                'pnl_percent': take_profit_result['profit_percent']
            }

        # 3. 트레일링 스톱 확인
        trailing_result = self.calculate_trailing_stop(
            entry_price,
            highest_price,
            current_price
        )
        if trailing_result['should_stop']:
            return {
                'should_close': True,
                'reason': '트레일링 스톱 발동',
                'pnl_percent': ((current_price - entry_price) / entry_price) * 100
            }

        # 4. 장 마감 시간 확인 (15:20 이후)
        if current_time:
            market_close_time = time(15, 20)
            if current_time.time() >= market_close_time:
                overnight_result = self.check_overnight_eligibility(
                    entry_price,
                    current_price
                )
                if not overnight_result['should_hold']:
                    return {
                        'should_close': True,
                        'reason': f"장 마감: {overnight_result['reason']}",
                        'pnl_percent': ((current_price - entry_price) / entry_price) * 100
                    }

        # 청산 조건 미충족
        return {
            'should_close': False,
            'reason': None,
            'pnl_percent': ((current_price - entry_price) / entry_price) * 100
        }


# 사용 예시
if __name__ == "__main__":
    # 테스트용 설정
    config = {
        'stop_loss_percent': 2.5,
        'take_profit_percent': 5.0,
        'trailing_stop': True,
        'trailing_stop_percent': 1.5,
        'max_position_size': 1000000,
        'max_positions': 5,
        'overnight_hold': False,
        'overnight_min_profit': 2.0,
        'daily_loss_limit': -5.0
    }

    risk_manager = RiskManager(config)

    # 포지션 크기 계산 예시
    position = risk_manager.calculate_position_size(
        stock_price=10000,
        account_balance=10000000,
        risk_percent=2.0
    )
    print("포지션 크기:", position)

    # 손절 확인 예시
    stop_loss = risk_manager.check_stop_loss(
        entry_price=10000,
        current_price=9700
    )
    print("손절 확인:", stop_loss)

    # 비중 상한 테스트
    print("\n--- 비중 상한 테스트 ---")

    # 케이스 1: 신규 매수 - 비중 상한 이내
    result = risk_manager.check_stock_concentration(
        current_invested=0,
        new_order_amount=1000000,
        total_account_value=10000000
    )
    print(f"신규 매수 (10%): allowed={result['allowed']}, "
          f"remaining={result['remaining_amount']:,.0f}원")

    # 케이스 2: 추가 매수 - 비중 상한 이내
    result = risk_manager.check_stock_concentration(
        current_invested=1000000,
        new_order_amount=500000,
        total_account_value=10000000
    )
    print(f"추가 매수 (15%): allowed={result['allowed']}, "
          f"remaining={result['remaining_amount']:,.0f}원")

    # 케이스 3: 추가 매수 - 비중 상한 초과
    result = risk_manager.check_stock_concentration(
        current_invested=1500000,
        new_order_amount=1000000,
        total_account_value=10000000
    )
    print(f"추가 매수 (25%): allowed={result['allowed']}, "
          f"remaining={result['remaining_amount']:,.0f}원")

    # 케이스 4: 이미 비중 상한 도달
    result = risk_manager.check_stock_concentration(
        current_invested=2000000,
        new_order_amount=100000,
        total_account_value=10000000
    )
    print(f"상한 도달 (20%): allowed={result['allowed']}, "
          f"remaining={result['remaining_amount']:,.0f}원, "
          f"ratio={result['current_ratio']:.1%}")
