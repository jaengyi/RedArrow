"""
기술적 지표 계산 모듈

이동평균선, MACD, 스토캐스틱, OBV 등의 기술적 지표를 계산합니다.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


class TechnicalIndicators:
    """기술적 지표 계산 클래스"""

    def __init__(self):
        """초기화"""
        pass

    def calculate_ma(self, data: pd.Series, period: int) -> pd.Series:
        """
        이동평균선 계산

        Args:
            data: 가격 데이터 (Series)
            period: 이동평균 기간

        Returns:
            이동평균선 값 (Series)
        """
        return data.rolling(window=period).mean()

    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        지수이동평균선 계산

        Args:
            data: 가격 데이터 (Series)
            period: 이동평균 기간

        Returns:
            지수이동평균선 값 (Series)
        """
        return data.ewm(span=period, adjust=False).mean()

    def calculate_macd(
        self,
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """
        MACD 지표 계산

        Args:
            data: 가격 데이터 (Series)
            fast_period: 빠른 EMA 기간 (기본: 12)
            slow_period: 느린 EMA 기간 (기본: 26)
            signal_period: 시그널 라인 기간 (기본: 9)

        Returns:
            {'macd': MACD 라인, 'signal': 시그널 라인, 'histogram': 히스토그램}
        """
        fast_ema = self.calculate_ema(data, fast_period)
        slow_ema = self.calculate_ema(data, slow_period)

        macd_line = fast_ema - slow_ema
        signal_line = self.calculate_ema(macd_line, signal_period)
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    def calculate_stochastic(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """
        스토캐스틱 지표 계산

        Args:
            high: 고가 데이터 (Series)
            low: 저가 데이터 (Series)
            close: 종가 데이터 (Series)
            k_period: %K 기간 (기본: 14)
            d_period: %D 기간 (기본: 3)

        Returns:
            {'%K': %K 라인, '%D': %D 라인}
        """
        # %K 계산
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)

        # %D 계산 (K의 이동평균)
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            '%K': k_percent,
            '%D': d_percent
        }

    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        OBV (On-Balance Volume) 지표 계산

        Args:
            close: 종가 데이터 (Series)
            volume: 거래량 데이터 (Series)

        Returns:
            OBV 값 (Series)
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    def calculate_volatility_breakout(
        self,
        open_price: float,
        prev_high: float,
        prev_low: float,
        k_value: float = 0.5
    ) -> float:
        """
        변동성 돌파 지표 계산 (Larry Williams의 변동성 돌파 전략)

        매수 기준가 = 당일 시가 + (전일 고가 - 전일 저가) × K

        Args:
            open_price: 당일 시가
            prev_high: 전일 고가
            prev_low: 전일 저가
            k_value: K 값 (기본: 0.5)

        Returns:
            변동성 돌파 기준가
        """
        prev_range = prev_high - prev_low
        breakout_price = open_price + (prev_range * k_value)

        return breakout_price

    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI (Relative Strength Index) 계산

        Args:
            data: 가격 데이터 (Series)
            period: RSI 기간 (기본: 14)

        Returns:
            RSI 값 (Series)
        """
        delta = data.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def detect_golden_cross(
        self,
        short_ma: pd.Series,
        long_ma: pd.Series
    ) -> pd.Series:
        """
        골든크로스 감지

        Args:
            short_ma: 단기 이동평균선
            long_ma: 장기 이동평균선

        Returns:
            골든크로스 발생 여부 (True/False Series)
        """
        # 이전 시점에서는 short_ma가 long_ma 아래에 있었고
        # 현재 시점에서는 short_ma가 long_ma 위로 올라간 경우
        prev_below = short_ma.shift(1) <= long_ma.shift(1)
        curr_above = short_ma > long_ma

        golden_cross = prev_below & curr_above

        return golden_cross

    def detect_dead_cross(
        self,
        short_ma: pd.Series,
        long_ma: pd.Series
    ) -> pd.Series:
        """
        데드크로스 감지

        Args:
            short_ma: 단기 이동평균선
            long_ma: 장기 이동평균선

        Returns:
            데드크로스 발생 여부 (True/False Series)
        """
        # 이전 시점에서는 short_ma가 long_ma 위에 있었고
        # 현재 시점에서는 short_ma가 long_ma 아래로 내려간 경우
        prev_above = short_ma.shift(1) >= long_ma.shift(1)
        curr_below = short_ma < long_ma

        dead_cross = prev_above & curr_below

        return dead_cross

    def check_price_above_ma(
        self,
        price: float,
        ma_values: pd.Series
    ) -> bool:
        """
        현재 가격이 이동평균선 위에 있는지 확인

        Args:
            price: 현재 가격
            ma_values: 이동평균선 값

        Returns:
            이동평균선 위에 있으면 True
        """
        if len(ma_values) == 0:
            return False

        current_ma = ma_values.iloc[-1]

        if pd.isna(current_ma):
            return False

        return price > current_ma

    def calculate_bollinger_bands(
        self,
        data: pd.Series,
        period: int = 20,
        num_std: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        볼린저 밴드 계산

        Args:
            data: 가격 데이터 (Series)
            period: 이동평균 기간 (기본: 20)
            num_std: 표준편차 배수 (기본: 2.0)

        Returns:
            {'upper': 상단 밴드, 'middle': 중간 밴드, 'lower': 하단 밴드}
        """
        middle_band = self.calculate_ma(data, period)
        std = data.rolling(window=period).std()

        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }


# 사용 예시
if __name__ == "__main__":
    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    test_data = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)

    # 지표 계산
    indicators = TechnicalIndicators()

    # 이동평균선
    ma20 = indicators.calculate_ma(test_data['close'], 20)
    print("MA(20):", ma20.tail())

    # MACD
    macd_result = indicators.calculate_macd(test_data['close'])
    print("\nMACD:", macd_result['macd'].tail())

    # 스토캐스틱
    stoch_result = indicators.calculate_stochastic(
        test_data['high'],
        test_data['low'],
        test_data['close']
    )
    print("\nStochastic %K:", stoch_result['%K'].tail())

    # OBV
    obv = indicators.calculate_obv(test_data['close'], test_data['volume'])
    print("\nOBV:", obv.tail())
