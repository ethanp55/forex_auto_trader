# import talib
import pandas as pd
import numpy as np


class DataFormatter(object):
    # def _add_fractal(self, df, i, look_back=2):
    #     if i >= look_back and i < df.shape[0] - look_back:
    #         lows = []
    #         highs = []

    #         for j in range(1, look_back + 1):
    #             prev_bid_low, prev_bid_high = df.loc[df.index[i - j], [
    #                 'Mid_Low', 'Mid_High']]
    #             future_bid_low, future_bid_high = df.loc[df.index[i + j], [
    #                 'Mid_Low', 'Mid_High']]

    #             lows.append(prev_bid_low)
    #             lows.append(future_bid_low)
    #             highs.append(prev_bid_high)
    #             highs.append(future_bid_high)

    #         bid_low, bid_high = df.loc[df.index[i], ['Mid_Low', 'Mid_High']]

    #         if bid_low < min(lows):
    #             return 1

    #         elif bid_high > max(highs):
    #             return 2

    #         else:
    #             return 0

    #     else:
    #         return np.nan

    # def _add_beep_boop(self, row):
    #     macdhist, ema50, mid_low, mid_high = row[[
    #         'macdhist', 'ema50', 'Mid_Low', 'Mid_High']]

    #     if float(macdhist) > 0 and float(mid_low) > float(ema50):
    #         return 1

    #     elif float(macdhist) < 0 and float(mid_high) < float(ema50):
    #         return 2

    #     else:
    #         return 0

    # def format_beep_boop_data(self, currency_pair, df):
    #     df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

    #     df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(
    #         df['Mid_Close'])
    #     df['ema200'] = talib.EMA(df['Mid_Close'], timeperiod=200)
    #     df['ema50'] = talib.EMA(df['Mid_Close'], timeperiod=50)
    #     df['adx'] = talib.ADX(df['Mid_High'], df['Mid_Low'],
    #                           df['Mid_Close'], timeperiod=14)
    #     df['rsi'] = talib.RSI(df['Mid_Close'], timeperiod=14)
    #     df['slowk'], df['slowd'] = talib.STOCH(
    #         df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
    #     cols = df.columns
    #     df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric)

    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)
    #     df = df.iloc[df.shape[0] - 100:, :]
    #     df.reset_index(drop=True, inplace=True)

    #     df['beep_boop'] = df.apply(self._add_beep_boop, axis=1)
    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)

    #     df['fractal'] = [self._add_fractal(
    #         df, i, look_back=3) for i in range(df.shape[0])]
    #     last_three_rows = df.iloc[-3:, :]
    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)

    #     df = df.append(last_three_rows, ignore_index=True)
    #     df.reset_index(drop=True, inplace=True)

    #     return df

    # def format_cnn_data(self, currency_pair, df, look_back_size=50):
    #     df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')
    #     df['sin_hour'] = np.sin(2 * np.pi * df['Date'].dt.hour / 24)
    #     df['cos_hour'] = np.cos(2 * np.pi * df['Date'].dt.hour / 24)
    #     df['sin_day'] = np.sin(2 * np.pi * df['Date'].dt.day / 7)
    #     df['cos_day'] = np.cos(2 * np.pi * df['Date'].dt.day / 7)
    #     df['sin_month'] = np.sin(2 * np.pi * df['Date'].dt.month / 12)
    #     df['cos_month'] = np.cos(2 * np.pi * df['Date'].dt.month / 12)
    #     dates = df.iloc[df.shape[0] - look_back_size:, 0]
    #     df.drop('Date', axis=1, inplace=True)

    #     df['rsi'] = talib.RSI(df['Mid_Close'])
    #     df['williams'] = talib.WILLR(
    #         df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
    #     df['wma'] = talib.WMA(df['Mid_Close'])
    #     df['ema1'] = talib.EMA(df['Mid_Close'])
    #     df['ema2'] = talib.EMA(df['Mid_Close'], timeperiod=60)
    #     df['sma1'] = talib.SMA(df['Mid_Close'])
    #     df['sma2'] = talib.SMA(df['Mid_Close'], timeperiod=60)
    #     df['tema'] = talib.TEMA(df['Mid_Close'])
    #     df['cci'] = talib.CCI(df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
    #     df['cmo'] = talib.CMO(df['Mid_Close'])
    #     df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(
    #         df['Mid_Close'])
    #     df['ppo'] = talib.PPO(df['Mid_Close'])
    #     df['roc'] = talib.ROC(df['Mid_Close'])
    #     df = df.astype(float)

    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)
    #     df = df.iloc[df.shape[0] - 100:, :]
    #     df.reset_index(drop=True, inplace=True)

    #     df['fractal'] = [self._add_fractal(df, i) for i in range(df.shape[0])]
    #     last_two_rows = df.iloc[-2:, :]
    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)

    #     df = df.append(last_two_rows, ignore_index=True)
    #     df.reset_index(drop=True, inplace=True)

    #     df = df.iloc[df.shape[0] - look_back_size:, :]
    #     df.reset_index(drop=True, inplace=True)

    #     price_data = df[['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close',
    #                      'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'fractal']]
    #     df.drop(['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low',
    #             'Ask_Close', 'Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close', 'fractal'], axis=1, inplace=True)
    #     df.reset_index(drop=True, inplace=True)

    #     gasf_transformer = GramianAngularField(method='summation')
    #     gasf_data = gasf_transformer.transform(df)

    #     print('Second to last date for current cnn sequence on ' +
    #           str(currency_pair) + ': ' + str(dates.iloc[-2]))
    #     print('Last date for current cnn sequence on ' +
    #           str(currency_pair) + ': ' + str(dates.iloc[-1]))
    #     print('Data shape: ' + str(gasf_data.shape))

    #     return gasf_data, price_data

    def format_stoch_macd_data(self, currency_pair, df):
        def psar(barsdata, iaf=0.02, maxaf=0.2):
            length = len(barsdata)
            high = list(barsdata['Mid_High'])
            low = list(barsdata['Mid_Low'])
            close = list(barsdata['Mid_Close'])
            psar = close[0:len(close)]
            bull = True
            af = iaf
            hp = high[0]
            lp = low[0]
            for i in range(2, length):
                if bull:
                    psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
                else:
                    psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
                reverse = False
                if bull:
                    if low[i] < psar[i]:
                        bull = False
                        reverse = True
                        psar[i] = hp
                        lp = low[i]
                        af = iaf
                else:
                    if high[i] > psar[i]:
                        bull = True
                        reverse = True
                        psar[i] = lp
                        hp = high[i]
                        af = iaf
                if not reverse:
                    if bull:
                        if high[i] > hp:
                            hp = high[i]
                            af = min(af + iaf, maxaf)
                        if low[i - 1] < psar[i]:
                            psar[i] = low[i - 1]
                        if low[i - 2] < psar[i]:
                            psar[i] = low[i - 2]
                    else:
                        if low[i] < lp:
                            lp = low[i]
                            af = min(af + iaf, maxaf)
                        if high[i - 1] > psar[i]:
                            psar[i] = high[i - 1]
                        if high[i - 2] > psar[i]:
                            psar[i] = high[i - 2]
            return psar

        def atr(barsdata, lookback=14):
            high_low = barsdata['Mid_High'] - barsdata['Mid_Low']
            high_close = np.abs(
                barsdata['Mid_High'] - barsdata['Mid_Close'].shift())
            low_close = np.abs(
                barsdata['Mid_Low'] - barsdata['Mid_Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)

            return true_range.rolling(lookback).sum() / lookback

        def rsi(barsdata, periods=14):
            close_delta = barsdata['Mid_Close'].diff()

            up = close_delta.clip(lower=0)
            down = -1 * close_delta.clip(upper=0)
            ma_up = up.ewm(com=periods - 1, adjust=True,
                           min_periods=periods).mean()
            ma_down = down.ewm(com=periods - 1, adjust=True,
                               min_periods=periods).mean()

            rsi = ma_up / ma_down
            rsi = 100 - (100/(1 + rsi))

            return rsi

        def adx(high, low, close, lookback=14):
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0

            tr1 = pd.DataFrame(high - low)
            tr2 = pd.DataFrame(abs(high - close.shift(1)))
            tr3 = pd.DataFrame(abs(low - close.shift(1)))
            frames = [tr1, tr2, tr3]
            tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
            atr = tr.rolling(lookback).mean()

            plus_di = 100 * (plus_dm.ewm(alpha=1/lookback).mean() / atr)
            minus_di = abs(100 * (minus_dm.ewm(alpha=1/lookback).mean() / atr))
            dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
            adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
            adx_smooth = adx.ewm(alpha=1/lookback).mean()

            return adx_smooth

        def stoch(high, low, close, lookback=14):
            high_lookback = high.rolling(lookback).max()
            low_lookback = low.rolling(lookback).min()
            slow_k = (close - low_lookback) * 100 / \
                (high_lookback - low_lookback)
            slow_d = slow_k.rolling(3).mean()

            return slow_k, slow_d

        def stoch_rsi(data, k_window=3, d_window=3, window=14):
            min_val = data.rolling(window=window, center=False).min()
            max_val = data.rolling(window=window, center=False).max()

            stoch = ((data - min_val) / (max_val - min_val)) * 100

            slow_k = stoch.rolling(window=k_window, center=False).mean()

            slow_d = slow_k.rolling(window=d_window, center=False).mean()

            return slow_k, slow_d

        def n_macd(macd, macdsignal, lookback=50):
            n_macd = 2 * (((macd - macd.rolling(lookback).min()) /
                          (macd.rolling(lookback).max() - macd.rolling(lookback).min()))) - 1
            n_macdsignal = 2 * (((macdsignal - macdsignal.rolling(lookback).min()) / (
                macdsignal.rolling(lookback).max() - macdsignal.rolling(lookback).min()))) - 1

            return n_macd, n_macdsignal

        def chop(df, lookback=14):
            atr1 = atr(df, lookback=1)
            high, low = df['Mid_High'], df['Mid_Low']

            chop = np.log10(atr1.rolling(lookback).sum(
            ) / (high.rolling(lookback).max() - low.rolling(lookback).min())) / np.log10(lookback)

            return chop

        def vo(volume, short_lookback=18, long_lookback=36):
            short_ema = pd.Series.ewm(volume, span=short_lookback).mean()
            long_ema = pd.Series.ewm(volume, span=long_lookback).mean()

            volume_oscillator = (short_ema - long_ema) / long_ema

            return volume_oscillator

        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        df['sin_hour'] = np.sin(2 * np.pi * df['Date'].dt.hour / 24)
        df['cos_hour'] = np.cos(2 * np.pi * df['Date'].dt.hour / 24)
        df['sin_day'] = np.sin(2 * np.pi * df['Date'].dt.day / 7)
        df['cos_day'] = np.cos(2 * np.pi * df['Date'].dt.day / 7)

        cols = df.columns
        df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric)

        df['ema200'] = pd.Series.ewm(df['Mid_Close'], span=200).mean()
        df['ema100'] = pd.Series.ewm(df['Mid_Close'], span=100).mean()
        df['ema50'] = pd.Series.ewm(df['Mid_Close'], span=50).mean()
        df['ema25'] = pd.Series.ewm(df['Mid_Close'], span=25).mean()

        df['atr'] = atr(df)
        df['rsi'] = rsi(df)
        df['rsi_sma'] = df['rsi'].rolling(100).mean()
        df['adx'] = adx(df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
        df['macd'] = pd.Series.ewm(df['Mid_Close'], span=12).mean(
        ) - pd.Series.ewm(df['Mid_Close'], span=26).mean()
        df['macdsignal'] = pd.Series.ewm(df['macd'], span=9).mean()
        df['n_macd'], df['n_macdsignal'] = n_macd(df['macd'], df['macdsignal'])
        df['slowk'], df['slowd'] = stoch(
            df['Mid_High'], df['Mid_Low'], df['Mid_Close'])
        df['slowk_rsi'], df['slowd_rsi'] = stoch_rsi(df['rsi'])

        df['sar'] = psar(df)

        df['chop14'] = chop(df)
        df['chop36'] = chop(df, lookback=36)

        df['vo'] = vo(df['Volume'])

        cols = df.columns
        df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        # df = df.iloc[df.shape[0] - 100:, :]
        # df.reset_index(drop=True, inplace=True)

        return df
