import logging
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from pattern_detector import (
    detect_cup_and_handle,
    detect_flag,
    detect_pennant,
    detect_harmonic,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)

class TradingStrategy:
    def __init__(self, asset: str, data_dir: Path):
        self.asset = asset
        self.data_dir = Path(data_dir)
        self.model = None

    def load_data(self) -> pd.DataFrame:
        path = self.data_dir / f"{self.asset}.csv"
        df = pd.read_csv(path)
        return df

    def features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema'] = df['Close'].ewm(span=10, adjust=False).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['macd'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['bollinger_high'] = df['Close'].rolling(window=20).mean() + 2*df['Close'].rolling(window=20).std()
        df['bollinger_low'] = df['Close'].rolling(window=20).mean() - 2*df['Close'].rolling(window=20).std()
        df['cup_handle'] = df.apply(lambda row: detect_cup_and_handle(df.loc[:row.name]), axis=1)
        df['flag'] = df.apply(lambda row: detect_flag(df.loc[:row.name]), axis=1)
        df['pennant'] = df.apply(lambda row: detect_pennant(df.loc[:row.name]), axis=1)
        df['harmonic'] = df.apply(lambda row: 1 if detect_harmonic(df.loc[:row.name]) else 0, axis=1)
        df = df.dropna()
        return df

    def train(self):
        df = self.features(self.load_data())
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        X = df[['ema','rsi','macd','signal','bollinger_high','bollinger_low','cup_handle','flag','pennant','harmonic']]
        y = df['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        models = {
            'rf': RandomForestClassifier(n_estimators=100),
            'lr': LogisticRegression(max_iter=200)
        }
        best_acc = 0
        best_model = None
        for name, model in models.items():
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            acc = accuracy_score(y_test, pred)
            logger.info("%s accuracy: %.2f", name, acc)
            if acc > best_acc:
                best_acc = acc
                best_model = model
        self.model = best_model
        logger.info("Selected model: %s", type(self.model).__name__)

    def predict_signal(self, df: pd.DataFrame) -> int:
        if self.model is None:
            raise RuntimeError('Model not trained')
        feat_df = self.features(df.tail(30))
        X = feat_df[['ema','rsi','macd','signal','bollinger_high','bollinger_low','cup_handle','flag','pennant','harmonic']].tail(1)
        return int(self.model.predict(X)[0])
