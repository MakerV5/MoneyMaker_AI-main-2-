import pandas as pd


def detect_cup_and_handle(df: pd.DataFrame) -> bool:
    window = 40
    if len(df) < window:
        return False
    prices = df['Close'].tail(window).reset_index(drop=True)
    mid = prices.idxmin()
    left_max = prices[:mid].max()
    right_max = prices[mid:].max()
    if mid == 0 or mid == window - 1:
        return False
    depth = (left_max + right_max) / 2 - prices[mid]
    return depth > 0 and abs(left_max - right_max) / max(left_max, right_max) < 0.1


def detect_flag(df: pd.DataFrame) -> bool:
    if len(df) < 10:
        return False
    segment = df['Close'].tail(10)
    trend = segment.iloc[-1] - segment.iloc[0]
    return abs(trend) < segment.std() * 2


def detect_pennant(df: pd.DataFrame) -> bool:
    if len(df) < 10:
        return False
    highs = df['High'].tail(10)
    lows = df['Low'].tail(10)
    return highs.is_monotonic_decreasing and lows.is_monotonic_increasing


def detect_harmonic(df: pd.DataFrame) -> str | None:
    if len(df) < 5:
        return None
    segment = df['Close'].tail(5).reset_index(drop=True)
    a, b, c, d, e = segment
    ab = abs(b - a)
    bc = abs(c - b)
    cd = abs(d - c)
    de = abs(e - d)
    ratio1 = bc / ab if ab else 0
    ratio2 = cd / bc if bc else 0
    ratio3 = de / cd if cd else 0
    if abs(ratio1 - 0.618) < 0.1 and abs(ratio2 - 0.618) < 0.1:
        if abs(ratio3 - 1.27) < 0.2:
            return 'Gartley'
        if abs(ratio3 - 1.618) < 0.2:
            return 'Butterfly'
    return None
