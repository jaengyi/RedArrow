"""
종목 선정 모듈

단기투자를 위한 종목 선정 로직을 구현합니다.
- 거래대금 상위 종목 필터링
- 기술적 지표 기반 선정
- 변동성 및 수급 분석
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from ..indicators.technical_indicators import TechnicalIndicators


class StockSelector:
    """종목 선정 클래스"""

    def __init__(self, config: Dict):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.indicators = TechnicalIndicators()

        # 설정값 로드
        self.top_volume_count = config.get('top_volume_count', 30)
        self.volume_surge_threshold = config.get('volume_surge_threshold', 2.0)
        self.k_value = config.get('k_value', 0.5)

        # 이동평균 기간
        self.ma_periods = config.get('ma_periods', {
            'short': 5,
            'medium': 20
        })

        # MACD 설정
        self.macd_config = config.get('macd', {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        })

        # 스토캐스틱 설정
        self.stochastic_config = config.get('stochastic', {
            'k_period': 14,
            'd_period': 3,
            'oversold': 20,
            'overbought': 80
        })

    def filter_by_volume_amount(
        self,
        stock_data: pd.DataFrame,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        거래대금 상위 종목 필터링

        Args:
            stock_data: 종목 데이터 (DataFrame)
                컬럼: code, name, price, volume, amount, change_rate 등
            top_n: 상위 N개 종목 (None이면 설정값 사용)

        Returns:
            거래대금 상위 종목 DataFrame
        """
        if top_n is None:
            top_n = self.top_volume_count

        # 거래대금 기준 내림차순 정렬
        sorted_stocks = stock_data.sort_values('amount', ascending=False)

        return sorted_stocks.head(top_n)

    def detect_volume_surge(
        self,
        current_volume: float,
        avg_volume: float,
        threshold: Optional[float] = None
    ) -> bool:
        """
        거래량 폭증 감지

        Args:
            current_volume: 현재 거래량
            avg_volume: 평균 거래량
            threshold: 폭증 기준 배수 (None이면 설정값 사용)

        Returns:
            거래량 폭증 여부
        """
        if threshold is None:
            threshold = self.volume_surge_threshold

        if avg_volume == 0:
            return False

        volume_ratio = current_volume / avg_volume

        return volume_ratio >= threshold

    def check_ma_breakout(
        self,
        price_data: pd.Series,
        current_price: float,
        ma_period: int = 20
    ) -> bool:
        """
        이동평균선 돌파 확인

        Args:
            price_data: 가격 데이터 (Series)
            current_price: 현재 가격
            ma_period: 이동평균 기간

        Returns:
            이동평균선 돌파 여부
        """
        ma = self.indicators.calculate_ma(price_data, ma_period)

        if len(ma) == 0 or pd.isna(ma.iloc[-1]):
            return False

        # 현재 가격이 이동평균선 위에 있는지 확인
        return current_price > ma.iloc[-1]

    def check_golden_cross(
        self,
        price_data: pd.Series,
        short_period: int = 5,
        long_period: int = 20
    ) -> bool:
        """
        골든크로스 발생 확인

        Args:
            price_data: 가격 데이터 (Series)
            short_period: 단기 이동평균 기간
            long_period: 장기 이동평균 기간

        Returns:
            골든크로스 발생 여부
        """
        short_ma = self.indicators.calculate_ma(price_data, short_period)
        long_ma = self.indicators.calculate_ma(price_data, long_period)

        golden_cross = self.indicators.detect_golden_cross(short_ma, long_ma)

        if len(golden_cross) == 0:
            return False

        # 최근 골든크로스 발생 여부
        return golden_cross.iloc[-1]

    def check_volatility_breakout(
        self,
        open_price: float,
        prev_high: float,
        prev_low: float,
        current_price: float
    ) -> bool:
        """
        변동성 돌파 확인

        Args:
            open_price: 당일 시가
            prev_high: 전일 고가
            prev_low: 전일 저가
            current_price: 현재 가격

        Returns:
            변동성 돌파 여부
        """
        breakout_price = self.indicators.calculate_volatility_breakout(
            open_price, prev_high, prev_low, self.k_value
        )

        return current_price >= breakout_price

    def check_macd_signal(self, price_data: pd.Series) -> Dict[str, bool]:
        """
        MACD 매수/매도 신호 확인

        Args:
            price_data: 가격 데이터 (Series)

        Returns:
            {'buy': 매수 신호, 'sell': 매도 신호}
        """
        macd_result = self.indicators.calculate_macd(
            price_data,
            fast_period=self.macd_config['fast_period'],
            slow_period=self.macd_config['slow_period'],
            signal_period=self.macd_config['signal_period']
        )

        macd_line = macd_result['macd']
        signal_line = macd_result['signal']

        if len(macd_line) < 2:
            return {'buy': False, 'sell': False}

        # 매수 신호: MACD가 시그널선을 상향 돌파
        buy_signal = (
            macd_line.iloc[-2] <= signal_line.iloc[-2] and
            macd_line.iloc[-1] > signal_line.iloc[-1]
        )

        # 매도 신호: MACD가 시그널선을 하향 돌파
        sell_signal = (
            macd_line.iloc[-2] >= signal_line.iloc[-2] and
            macd_line.iloc[-1] < signal_line.iloc[-1]
        )

        return {'buy': buy_signal, 'sell': sell_signal}

    def check_stochastic_signal(
        self,
        high_data: pd.Series,
        low_data: pd.Series,
        close_data: pd.Series
    ) -> Dict[str, bool]:
        """
        스토캐스틱 매수/매도 신호 확인

        Args:
            high_data: 고가 데이터 (Series)
            low_data: 저가 데이터 (Series)
            close_data: 종가 데이터 (Series)

        Returns:
            {'buy': 매수 신호, 'oversold': 과매도, 'overbought': 과매수}
        """
        stoch_result = self.indicators.calculate_stochastic(
            high_data,
            low_data,
            close_data,
            k_period=self.stochastic_config['k_period'],
            d_period=self.stochastic_config['d_period']
        )

        k_line = stoch_result['%K']
        d_line = stoch_result['%D']

        if len(k_line) < 2:
            return {'buy': False, 'oversold': False, 'overbought': False}

        # 매수 신호: %K가 %D를 상향 돌파
        buy_signal = (
            k_line.iloc[-2] <= d_line.iloc[-2] and
            k_line.iloc[-1] > d_line.iloc[-1]
        )

        # 과매도 구간 탈출
        oversold_exit = (
            k_line.iloc[-2] <= self.stochastic_config['oversold'] and
            k_line.iloc[-1] > self.stochastic_config['oversold']
        )

        # 과매수 구간
        overbought = k_line.iloc[-1] >= self.stochastic_config['overbought']

        return {
            'buy': buy_signal,
            'oversold': oversold_exit,
            'overbought': overbought
        }

    def check_obv_trend(
        self,
        close_data: pd.Series,
        volume_data: pd.Series
    ) -> bool:
        """
        OBV 상승 추세 확인

        Args:
            close_data: 종가 데이터 (Series)
            volume_data: 거래량 데이터 (Series)

        Returns:
            OBV 상승 여부
        """
        obv = self.indicators.calculate_obv(close_data, volume_data)

        if len(obv) < 2:
            return False

        # OBV가 상승 중인지 확인
        return obv.iloc[-1] > obv.iloc[-2]

    def detect_order_book_imbalance(
        self,
        bid_volume: float,
        ask_volume: float
    ) -> Dict[str, any]:
        """
        호가창 불균형 감지

        Args:
            bid_volume: 매수 잔량
            ask_volume: 매도 잔량

        Returns:
            {'imbalance': 불균형 비율, 'signal': 신호 타입}
        """
        total_volume = bid_volume + ask_volume

        if total_volume == 0:
            return {'imbalance': 0, 'signal': 'neutral'}

        # 매도 잔량이 더 많은 경우 (역설적으로 상승 가능성)
        if ask_volume > bid_volume:
            imbalance_ratio = ask_volume / total_volume
            if imbalance_ratio > 0.6:  # 60% 이상 매도 잔량
                return {'imbalance': imbalance_ratio, 'signal': 'buy_opportunity'}

        # 매수 잔량이 더 많은 경우 (매수세 강함)
        if bid_volume > ask_volume:
            imbalance_ratio = bid_volume / total_volume
            if imbalance_ratio > 0.6:
                return {'imbalance': imbalance_ratio, 'signal': 'strong_buy'}

        return {'imbalance': 0.5, 'signal': 'neutral'}

    def detect_support_at_ma(
        self,
        price_data: pd.Series,
        current_price: float,
        ma_period: int = 20,
        tolerance: float = 0.01
    ) -> bool:
        """
        눌림목 형성 감지 (이동평균선 지지)

        Args:
            price_data: 가격 데이터 (Series)
            current_price: 현재 가격
            ma_period: 이동평균 기간
            tolerance: 허용 오차 (1% 기본)

        Returns:
            눌림목 형성 여부
        """
        ma = self.indicators.calculate_ma(price_data, ma_period)

        if len(ma) == 0 or pd.isna(ma.iloc[-1]):
            return False

        ma_value = ma.iloc[-1]

        # 현재 가격이 이동평균선 근처에서 지지받는지 확인
        price_diff_ratio = abs(current_price - ma_value) / ma_value

        return price_diff_ratio <= tolerance

    def select_stocks(
        self,
        stock_data: pd.DataFrame,
        price_history: Dict[str, pd.DataFrame]
    ) -> List[Dict]:
        """
        종목 선정 메인 로직

        Args:
            stock_data: 현재 종목 데이터 (DataFrame)
                필수 컬럼: code, name, price, volume, amount, change_rate,
                         open, high, low, close, prev_high, prev_low
            price_history: 종목별 과거 가격 데이터 (Dict[종목코드: DataFrame])
                DataFrame 컬럼: open, high, low, close, volume

        Returns:
            선정된 종목 리스트 (각 종목은 Dict 형태)
        """
        selected_stocks = []

        # 1. 거래대금 상위 종목 필터링
        top_stocks = self.filter_by_volume_amount(stock_data)

        for _, stock in top_stocks.iterrows():
            stock_code = stock['code']
            current_price = stock['price']

            # 과거 데이터가 없으면 스킵
            if stock_code not in price_history:
                continue

            history = price_history[stock_code]

            if len(history) < 20:  # 최소 20일 데이터 필요
                continue

            # 선정 점수 계산
            score = 0
            signals = {}

            # 2. 거래량 폭증 확인
            avg_volume = history['volume'].mean()
            volume_surge = self.detect_volume_surge(
                stock['volume'],
                avg_volume
            )
            if volume_surge:
                score += 3
                signals['volume_surge'] = True

            # 3. 이동평균선 확인
            ma_20_breakout = self.check_ma_breakout(
                history['close'],
                current_price,
                20
            )
            if ma_20_breakout:
                score += 2
                signals['ma_20_above'] = True

            # 4. 골든크로스 확인
            golden_cross = self.check_golden_cross(
                history['close'],
                self.ma_periods['short'],
                self.ma_periods['medium']
            )
            if golden_cross:
                score += 3
                signals['golden_cross'] = True

            # 5. 변동성 돌파 확인
            volatility_breakout = self.check_volatility_breakout(
                stock['open'],
                stock['prev_high'],
                stock['prev_low'],
                current_price
            )
            if volatility_breakout:
                score += 2
                signals['volatility_breakout'] = True

            # 6. MACD 신호 확인
            macd_signal = self.check_macd_signal(history['close'])
            if macd_signal['buy']:
                score += 2
                signals['macd_buy'] = True

            # 7. 스토캐스틱 신호 확인
            stoch_signal = self.check_stochastic_signal(
                history['high'],
                history['low'],
                history['close']
            )
            if stoch_signal['buy'] or stoch_signal['oversold']:
                score += 2
                signals['stochastic_buy'] = True

            # 8. OBV 확인
            obv_rising = self.check_obv_trend(
                history['close'],
                history['volume']
            )
            if obv_rising:
                score += 1
                signals['obv_rising'] = True

            # 9. 눌림목 형성 확인
            support_at_ma = self.detect_support_at_ma(
                history['close'],
                current_price,
                20
            )
            if support_at_ma:
                score += 1
                signals['support_at_ma'] = True

            # 선정 기준: 점수 5점 이상
            if score >= 5:
                selected_stocks.append({
                    'code': stock_code,
                    'name': stock['name'],
                    'price': current_price,
                    'volume': stock['volume'],
                    'amount': stock['amount'],
                    'change_rate': stock['change_rate'],
                    'score': score,
                    'signals': signals,
                    'timestamp': datetime.now()
                })

        # 점수 순으로 정렬
        selected_stocks.sort(key=lambda x: x['score'], reverse=True)

        return selected_stocks


# 사용 예시
if __name__ == "__main__":
    # 테스트용 설정
    config = {
        'top_volume_count': 30,
        'volume_surge_threshold': 2.0,
        'k_value': 0.5,
        'ma_periods': {'short': 5, 'medium': 20},
        'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
        'stochastic': {'k_period': 14, 'd_period': 3, 'oversold': 20, 'overbought': 80}
    }

    selector = StockSelector(config)
    print("종목 선정 시스템 초기화 완료")
