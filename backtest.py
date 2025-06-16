import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from src.strategy import TradingStrategy


def run_backtest(path: Path):
    df = pd.read_csv(path)
    strategy = TradingStrategy(path.stem, path.parent)
    strategy.train()
    balance = 0.0
    equity = []
    position = None
    entry = 0.0
    for i in range(len(df) - 1):
        window = df.iloc[: i + 1]
        signal = strategy.predict_signal(window)
        price = df.loc[i, 'Close']
        if signal == 1 and position is None:
            position = 'long'
            entry = price
        elif signal == 0 and position == 'long':
            balance += price - entry
            position = None
        equity.append(balance + (price - entry if position else 0))
    dd = max(equity) - equity[-1] if equity else 0
    plt.figure()
    plt.plot(equity)
    plt.title('Equity Curve')
    out = Path('dashboard/static/backtests') / f'{path.stem}_equity.png'
    plt.savefig(out)
    plt.close()
    return balance, dd, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    args = parser.parse_args()
    bal, dd, out = run_backtest(args.csv)
    print(f'Profit: {bal:.2f}, Drawdown: {dd:.2f}, plot: {out}')


if __name__ == '__main__':
    main()
