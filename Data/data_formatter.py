import talib
import pandas as pd
import numpy as np
from TimeSeries.gaf import GramianAngularField


class DataFormatter(object):
    def _add_fractal(self, df, i, look_back=2):
        if i >= look_back and i < df.shape[0] - look_back:
            lows = []
            highs = []

            for j in range(1, look_back + 1):
                prev_bid_low, prev_bid_high = df.loc[df.index[i - j], ['Mid_Low', 'Mid_High']]
                future_bid_low, future_bid_high = df.loc[df.index[i + j], ['Mid_Low', 'Mid_High']]

                lows.append(prev_bid_low)
                lows.append(future_bid_low)
                highs.append(prev_bid_high)
                highs.append(future_bid_high)

            bid_low, bid_high = df.loc[df.index[i], ['Mid_Low', 'Mid_High']]

            if bid_low < min(lows):
                return 1

            elif bid_high > max(highs):
                return 2

            else:
                return 0

        else:
            return np.nan

    def _add_beep_boop(self, df, i):
        macdhist, ema50, ema200, bid_low, bid_high = df.loc[df.index[i], ['macdhist', 'ema50', 'ema200', 'Mid_Low', 'Mid_High']]

        if macdhist > 0 and bid_low > ema50:
            return 1

        elif macdhist < 0 and bid_high < ema50:
            return 2

        else:
            return 0

    def format_beep_boop_data(self, currency_pair, df):
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Mid_Close'])
        df['ema200'] = talib.EMA(df['Mid_Close'], timeperiod=200)
        df['ema50'] = talib.EMA(df['Mid_Close'], timeperiod=50)
        df['atr'] = talib.ATR(df['Mid_High'], df['Mid_Low'], df['Mid_Close'], timeperiod=500)
        cols = df.columns
        df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[df.shape[0] - 100:, :]
        df.reset_index(drop=True, inplace=True)

        df['beep_boop'] = [self._add_beep_boop(df, i) for i in range(df.shape[0])]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df['fractal'] = [self._add_fractal(df, i, look_back=3) for i in range(df.shape[0])]
        last_three_rows = df.iloc[-3:, :]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df = df.append(last_three_rows, ignore_index=True)
        df.reset_index(drop=True, inplace=True)

        return df

    def format_cnn_data(self, currency_pair, df, look_back_size=50):
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')
        df['sin_hour'] = np.sin(2 * np.pi * df['Date'].dt.hour / 24)
        df['cos_hour'] = np.cos(2 * np.pi * df['Date'].dt.hour / 24)
        df['sin_day'] = np.sin(2 * np.pi * df['Date'].dt.day / 7)
        df['cos_day'] = np.cos(2 * np.pi * df['Date'].dt.day / 7)
        df['sin_month'] = np.sin(2 * np.pi * df['Date'].dt.month / 12)
        df['cos_month'] = np.cos(2 * np.pi * df['Date'].dt.month / 12)
        dates = df.iloc[df.shape[0] - look_back_size:, 0]
        df.drop('Date', axis=1, inplace=True)

        df['rsi'] = talib.RSI(df['Mid_Close'])
        df['williams'] = talib.WILLR(df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
        df['wma'] = talib.WMA(df['Mid_Close'])
        df['ema1'] = talib.EMA(df['Mid_Close'])
        df['ema2'] = talib.EMA(df['Mid_Close'], timeperiod=60)
        df['sma1'] = talib.SMA(df['Mid_Close'])
        df['sma2'] = talib.SMA(df['Mid_Close'], timeperiod=60)
        df['tema'] = talib.TEMA(df['Mid_Close'])
        df['cci'] = talib.CCI(df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
        df['cmo'] = talib.CMO(df['Mid_Close'])
        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Mid_Close'])
        df['ppo'] = talib.PPO(df['Mid_Close'])
        df['roc'] = talib.ROC(df['Mid_Close'])
        df = df.astype(float)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[df.shape[0] - 100:, :]
        df.reset_index(drop=True, inplace=True)

        df['fractal'] = [self._add_fractal(df, i) for i in range(df.shape[0])]
        last_two_rows = df.iloc[-2:, :]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df = df.append(last_two_rows, ignore_index=True)
        df.reset_index(drop=True, inplace=True)

        df = df.iloc[df.shape[0] - look_back_size:, :]
        df.reset_index(drop=True, inplace=True)

        price_data = df[['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'fractal']]
        df.drop(['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close', 'fractal'], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        gasf_transformer = GramianAngularField(method='summation')
        gasf_data = gasf_transformer.transform(df)

        print('Second to last date for current cnn sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-2]))
        print('Last date for current cnn sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-1]))
        print('Data shape: ' + str(gasf_data.shape))

        return gasf_data, price_data

    def format_stoch_macd_data(self, currency_pair, df):
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Mid_Close'])
        df['ema200'] = talib.EMA(df['Mid_Close'], timeperiod=200)
        df['slowk'], df['slowd'] = talib.STOCH(df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
        cols = df.columns
        df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[df.shape[0] - 100:, :]
        df.reset_index(drop=True, inplace=True)

        df['fractal'] = [self._add_fractal(df, i, look_back=3) for i in range(df.shape[0])]
        last_three_rows = df.iloc[-3:, :]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df = df.append(last_three_rows, ignore_index=True)
        df.reset_index(drop=True, inplace=True)

        return df
