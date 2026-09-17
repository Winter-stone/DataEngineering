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
        df['EMA'] = df.groupby("ticker")['close'].transform(
            lambda x: x.ewm(span=ema, adjust=False).mean())

        df["SMMA"] = df.groupby("ticker")['close'].transform(
            lambda x: x.ewm(alpha=1/smma, adjust=False).mean())

        df["ma_cross"] = np.where(df["EMA"] > df["SMMA"], 1, -1)

        df.drop(columns=["EMA", "SMMA"], inplace=True)
        df.dropna(inplace=True)

        return df

    def mean_reversion(self, df, window=14):
        
        df["returns"] = np.log(df["close"] / df.groupby("ticker")["close"].shift(1))

        df["mean_reversion"] = -np.sign(df.groupby("ticker")["returns"].transform(
            lambda x: x.rolling(window=window).mean()))

        df.drop(columns=["returns"], inplace=True)
        df.dropna(inplace=True)

        return df

    def relative_volume(self, df, period = 20):
        df["relative_volume"] = df.groupby("ticker")["volume"].transform(
            lambda x: (x / x.rolling(window=period).mean().shift(1)).round(1))       
        
        df["relative_volume"] = df["relative_volume"].fillna(0)
        
        return df
        
    def calculate_adx(self, df, period = 14):
        
        # 1. Grouped Shifts to prevent cross-ticker bleed
        high_shift = df.groupby("ticker")['high'].shift(1)
        low_shift = df.groupby("ticker")['low'].shift(1)
        close_shift = df.groupby("ticker")['close'].shift(1)

        # 2. Calculate Moves (Vectorized)
        df['up_move'] = df['high'] - high_shift
        df['down_move'] = low_shift - df['low']

        df['+dm'] = np.where((df['up_move'] > df['down_move']) & 
                             (df['up_move'] > 0), df['up_move'], 0)
        
        df['-dm'] = np.where((df['down_move'] > df['up_move']) & 
                             (df['down_move'] > 0), df['down_move'], 0)

        # 3. True Range (Vectorized)
        df['TR'] = np.maximum(
            df['high'] - df['low'], 
            np.maximum(
                abs(df['high'] - close_shift), 
                abs(df['low'] - close_shift)
            )
        )

        # 4. Wilder's Smoothing for TR and DM (Grouped)
        df['tr_smoothed'] = df.groupby("ticker")['TR'].transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )
        df['+dm_smoothed'] = df.groupby("ticker")['+dm'].transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )
        df['-dm_smoothed'] = df.groupby("ticker")['-dm'].transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )

        # 5. Directional Indices (Vectorized)
        df['+di'] = 100 * (df['+dm_smoothed'] / df['tr_smoothed'])
        df['-di'] = 100 * (df['-dm_smoothed'] / df['tr_smoothed'])
        df['DX'] = 100 * (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di']))

        # 6. Final adx and atr Smoothing (Grouped)
        df['adx'] = df.groupby("ticker")['DX'].transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )
        df['atr'] = df.groupby("ticker")['TR'].transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )
        
        df["adx"] = df["adx"].fillna(0)
        df["atr"] = df["atr"].fillna(0)

        # 7. Cleanup
        df.drop(columns=['up_move', 'down_move', 'TR', 'tr_smoothed', 
            '+dm_smoothed', '-dm_smoothed', '+dm', '-dm', 
            '+di', '-di', 'DX'], inplace=True)
        
        return df

    def calculate_rsi(self, df, period=14):
        
        # 1. Calculate delta grouped by ticker to prevent data bleed
        delta = df.groupby("ticker")['close'].diff()

        # 2. Separate Gains and Losses (Row-by-row, no groupby needed)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 3. Wilder's Smoothing grouped by ticker using transform
        avg_gain = gain.groupby(df["ticker"]).transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )

        avg_loss = loss.groupby(df["ticker"]).transform(
            lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        )

        # 4. Calculate RS (Vectorized)
        rs = avg_gain / avg_loss

        # 5. Calculate rsi
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(0)
        
        return df

    def calculate_daily_vwap(self, df, window = 20):

        df['htf_ema'] = df.groupby("ticker")['close'].transform(
            lambda x: x.ewm(span=(window * 10), adjust=False).mean())
        
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        df['pv'] = typical_price * df['volume']

        rolling_pv = df.groupby("ticker")['pv'].transform(
            lambda x: x.rolling(window=window, min_periods=1).sum())

        rolling_vol = df.groupby("ticker")['volume'].transform(
            lambda x: x.rolling(window=window, min_periods=1).sum())
        
        df['daily_vwap'] = rolling_pv / rolling_vol
        
        df.drop(columns=['pv'], inplace=True)

        return df