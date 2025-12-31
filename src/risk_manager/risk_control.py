"""
리스크 관리 모듈

손절매, 익절, 포지션 크기 결정 등 리스크 관리 기능을 제공합니다.
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime, time


class RiskManager:
    """리스크 관리 클래스"""

    def __init__(self, config: Dict):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config

        # 손절 설정
        self.stop_loss_percent = config.get('stop_loss_percent', 2.5)

        # 익절 설정
        self.take_profit_percent = config.get('take_profit_percent', 5.0)

        # 트레일링 스톱 설정
        self.trailing_stop = config.get('trailing_stop', True)
        self.trailing_stop_percent = config.get('trailing_stop_percent', 1.5)

        # 포지션 관리
        self.max_position_size = config.get('max_position_size', 1000000)
        self.max_positions = config.get('max_positions', 5)

        # 오버나이트 설정
        self.overnight_hold = config.get('overnight_hold', False)
        self.overnight_min_profit = config.get('overnight_min_profit', 2.0)

        # 일일 손실 제한
        self.daily_loss_limit = config.get('daily_loss_limit', -5.0)

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
        # 손실률 계산
        loss_percent = ((current_price - entry_price) / entry_price) * 100

        # 1. 퍼센트 기준 손절
        if loss_percent <= -self.stop_loss_percent:
            return {
                'should_stop': True,
                'reason': f'손실률 {self.stop_loss_percent}% 초과',
                'loss_percent': loss_percent
            }

        # 2. 이동평균선 이탈 손절
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
        if not self.trailing_stop:
            return {'should_stop': False, 'trailing_stop_price': None}

        # 최고가 대비 하락률 계산
        drop_from_high = ((current_price - highest_price) / highest_price) * 100

        # 트레일링 스톱 가격 계산
        trailing_stop_price = highest_price * (1 - self.trailing_stop_percent / 100)

        # 트레일링 스톱 발동 조건:
        # 1. 현재가가 최고가 대비 일정 % 하락
        # 2. 현재가가 매수가보다는 높아야 함 (손실 방지)
        should_stop = (
            drop_from_high <= -self.trailing_stop_percent and
            current_price > entry_price
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
        # 리스크 금액 계산 (계좌 잔고의 risk_percent%)
        risk_amount = account_balance * (risk_percent / 100)

        # 손절가 기준으로 매수 수량 계산
        # 리스크 금액 = 매수 수량 × 주가 × 손절률
        max_quantity = int(
            risk_amount / (stock_price * (self.stop_loss_percent / 100))
        )

        # 최대 포지션 크기 제한
        max_position_quantity = int(self.max_position_size / stock_price)
        quantity = min(max_quantity, max_position_quantity)

        # 실제 매수 금액
        amount = quantity * stock_price

        return {
            'quantity': quantity,
            'amount': amount,
            'risk_amount': risk_amount
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
