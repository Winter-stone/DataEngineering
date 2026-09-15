import numpy as np
import pandas as pd

class filters:
    
    def __init__(self, data):
        self.data = data

    def get_all_filters(self):
        data = self.data.copy()
        data = self.calculate_ma_crossover(data)
        data = self.mean_reversion(data)
        data = self.relative_volume(data)
        data = self.calculate_adx(data)
        data = self.calculate_rsi(data)
        data = self.calculate_daily_vwap(data)
        self.data = data.copy()
        return self.data

    def calculate_ma_crossover(self, df, smma = 89, ema = 5):
        df['EMA'] = df.close.ewm(span = ema, adjust = False).mean()
        df["SMMA"] = df.close.ewm(alpha = 1/smma, adjust = False).mean()
        df["ma_position"] = np.where(df["EMA"] > df["SMMA"], 1, -1)
        df.drop(columns = ["EMA", "SMMA"], inplace=True)
        df.dropna(inplace=True)

        return df

    def mean_reversion(self, df, window=14):
        df["returns"] = np.log(df["close"]/df["close"].shift(1))
        df["con_position"] = -np.sign(df['returns'].rolling(window).mean())
        df.dropna(inplace=True)

        return df

    def relative_volume(self, df, period = 20):
        df["RVOL"] = (df["volume"] / df["volume"].rolling(period).mean().shift(1)).round(1)
        return df

        
    def calculate_adx(self, df, period = 14):
        df['up_move'] = df['high'] - df['high'].shift(1)
        df['down_move'] = df['low'].shift(1) - df['low']

        df['+dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
        df['-dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

        df['TR'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))

        df['tr_smoothed'] = df['TR'].ewm(alpha=1/period, adjust = False).mean()
        df['+dm_smoothed'] = df['+dm'].ewm(alpha=1/period, adjust=False).mean()
        df['-dm_smoothed'] = df['-dm'].ewm(alpha=1/period, adjust=False).mean()

        df['+di'] = 100 * (df['+dm_smoothed'] / df['tr_smoothed'])
        df['-di'] = 100 * (df['-dm_smoothed'] / df['tr_smoothed'])

        df['DX'] = 100 * (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di']))

        df['ADX'] = df['DX'].ewm(alpha=1/period, adjust=False).mean()
        df["ATR"] = df["TR"].ewm(alpha=1/period, adjust=False).mean()
        
        df.drop(columns = ['up_move', 'down_move', 'TR', 'tr_smoothed', '+dm_smoothed', '-dm_smoothed', '+dm', '-dm',"+di", "-di", 'DX'], inplace=True)

        return df

    def calculate_rsi(self, df, period=14):
        delta = df['close'].diff()

        # 2. Separate Gains and Losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 3. Wilder's Smoothing (alpha = 1/period)
        # Using ewm with adjust=False mimics Wilder's recursive formula perfectly
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        # 4. Calculate RS
        rs = avg_gain / avg_loss

        # 5. Calculate RSI
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def calculate_daily_vwap(self, df, window = 20):

        df['htf_ema'] = df['Close'].ewm(span=(window * 10), adjust=False).mean()
        
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        pv = typical_price * df['Volume']
        
        rolling_pv = pv.rolling(window=window, min_periods=1).sum()
        rolling_vol = df['Volume'].rolling(window=window, min_periods=1).sum()
        df['daily_vwap'] = rolling_pv / rolling_vol

        return df