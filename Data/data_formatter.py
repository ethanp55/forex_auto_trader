import talib
import pandas as pd
import numpy as np
from pickle import load
from pyts.image import GramianAngularField


class DataFormatter(object):
    def __init__(self):
        eur_usd_scaler = load(open('Data/Files/eur_usd_rnn_scaler.pkl', 'rb'))
        gbp_chf_scaler = load(open('Data/Files/gbp_chf_rnn_scaler.pkl', 'rb'))
        usd_cad_scaler = load(open('Data/Files/usd_cad_rnn_scaler.pkl', 'rb'))
        aud_usd_scaler = load(open('Data/Files/aud_usd_rnn_scaler.pkl', 'rb'))
        nzd_usd_scaler = load(open('Data/Files/nzd_usd_rnn_scaler.pkl', 'rb'))
        self.scalers = {'EUR_USD': eur_usd_scaler, 'GBP_CHF': gbp_chf_scaler, 'USD_CAD': usd_cad_scaler, 'AUD_USD': aud_usd_scaler, 'NZD_USD': nzd_usd_scaler}

    def format_data(self, currency_pair, df):
        # Make sure the dates are formatted properly
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        # Add hour of day, day of week, and month of year (for additional features)
        # Use sine and cosine to keep the cyclic nature of hour, day, and month
        #  (December is closer to January than October, midnight is closer to 1 am than
        #  10 pm, etc.)
        df['sin_hour'] = np.sin(2 * np.pi * df['Date'].dt.hour / 24)
        df['cos_hour'] = np.cos(2 * np.pi * df['Date'].dt.hour / 24)
        df['sin_day'] = np.sin(2 * np.pi * df['Date'].dt.day / 7)
        df['cos_day'] = np.cos(2 * np.pi * df['Date'].dt.day / 7)
        df['sin_month'] = np.sin(2 * np.pi * df['Date'].dt.month / 12)
        df['cos_month'] = np.cos(2 * np.pi * df['Date'].dt.month / 12)

        # Bid technical indicators
        df['Bid_SMA1'] = talib.SMA(df['Bid_Close'], timeperiod=10)
        df['Bid_SMA1_Envelope_Upper'] = df['Bid_SMA1'] + (0.1 * df['Bid_SMA1'])
        df['Bid_SMA1_Envelope_Lower'] = df['Bid_SMA1'] - (0.1 * df['Bid_SMA1'])
        df['Bid_EMA1'] = talib.EMA(df['Bid_Close'], timeperiod=10)
        df['Bid_EMA1_Envelope_Upper'] = df['Bid_EMA1'] + (0.1 * df['Bid_EMA1'])
        df['Bid_EMA1_Envelope_Lower'] = df['Bid_EMA1'] - (0.1 * df['Bid_EMA1'])
        df['Bid_SMA2'] = talib.SMA(df['Bid_Close'], timeperiod=20)
        df['Bid_SMA2_Envelope_Upper'] = df['Bid_SMA2'] + (0.1 * df['Bid_SMA2'])
        df['Bid_SMA2_Envelope_Lower'] = df['Bid_SMA2'] - (0.1 * df['Bid_SMA2'])
        df['Bid_EMA2'] = talib.EMA(df['Bid_Close'], timeperiod=20)
        df['Bid_EMA2_Envelope_Upper'] = df['Bid_EMA2'] + (0.1 * df['Bid_EMA2'])
        df['Bid_EMA2_Envelope_Lower'] = df['Bid_EMA2'] - (0.1 * df['Bid_EMA2'])
        df['Bid_SMA3'] = talib.SMA(df['Bid_Close'], timeperiod=30)
        df['Bid_SMA3_Envelope_Upper'] = df['Bid_SMA3'] + (0.1 * df['Bid_SMA3'])
        df['Bid_SMA3_Envelope_Lower'] = df['Bid_SMA3'] - (0.1 * df['Bid_SMA3'])
        df['Bid_EMA3'] = talib.EMA(df['Bid_Close'], timeperiod=30)
        df['Bid_EMA3_Envelope_Upper'] = df['Bid_EMA3'] + (0.1 * df['Bid_EMA3'])
        df['Bid_EMA3_Envelope_Lower'] = df['Bid_EMA3'] - (0.1 * df['Bid_EMA3'])
        df['Bid_BB_Upper_Band'], df['Bid_BB_Middle_Band'], df['Bid_BB_Lower_Band'] = talib.BBANDS(
            df['Bid_Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        df['Bid_MACD'], df['Bid_MACD_Signal'], df['Bid_MACD_hist'] = talib.MACD(df['Bid_Close'],
                                                                                fastperiod=12,
                                                                                slowperiod=26,
                                                                                signalperiod=9)
        df['Bid_Parabollic_SAR'] = talib.SAR(df['Bid_High'], df['Bid_Low'], acceleration=0, maximum=0)
        df['Bid_Slowk'], df['Bid_Slowd'] = talib.STOCH(df['Bid_High'], df['Bid_Low'], df['Bid_Close'],
                                                       fastk_period=5, slowk_period=3,
                                                       slowk_matype=0, slowd_period=3,
                                                       slowd_matype=0)
        df['Bid_RSI'] = talib.RSI(df['Bid_Close'], timeperiod=14)
        df['Bid_Williams_Percent_Range'] = talib.WILLR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'],
                                                       timeperiod=14)
        df['Bid_ADX'] = talib.ADX(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)
        df['Bid_ADXR'] = talib.ADXR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)
        df['Bid_MOM'] = talib.MOM(df['Bid_Close'], timeperiod=10)
        df['Bid_BOP'] = talib.BOP(df['Bid_Open'], df['Bid_High'], df['Bid_Low'], df['Bid_Close'])
        df['Bid_AROONOSC'] = talib.AROONOSC(df['Bid_High'], df['Bid_Low'], timeperiod=14)
        df['Bid_ATR'] = talib.ATR(df['Bid_High'], df['Bid_Low'], df['Bid_Close'], timeperiod=14)

        # Ask technical indicators
        df['Ask_SMA1'] = talib.SMA(df['Ask_Close'], timeperiod=10)
        df['Ask_SMA1_Envelope_Upper'] = df['Ask_SMA1'] + (0.1 * df['Ask_SMA1'])
        df['Ask_SMA1_Envelope_Lower'] = df['Ask_SMA1'] - (0.1 * df['Ask_SMA1'])
        df['Ask_EMA1'] = talib.EMA(df['Ask_Close'], timeperiod=10)
        df['Ask_EMA1_Envelope_Upper'] = df['Ask_EMA1'] + (0.1 * df['Ask_EMA1'])
        df['Ask_EMA1_Envelope_Lower'] = df['Ask_EMA1'] - (0.1 * df['Ask_EMA1'])
        df['Ask_SMA2'] = talib.SMA(df['Ask_Close'], timeperiod=20)
        df['Ask_SMA2_Envelope_Upper'] = df['Ask_SMA2'] + (0.1 * df['Ask_SMA2'])
        df['Ask_SMA2_Envelope_Lower'] = df['Ask_SMA2'] - (0.1 * df['Ask_SMA2'])
        df['Ask_EMA2'] = talib.EMA(df['Ask_Close'], timeperiod=20)
        df['Ask_EMA2_Envelope_Upper'] = df['Ask_EMA2'] + (0.1 * df['Ask_EMA2'])
        df['Ask_EMA2_Envelope_Lower'] = df['Ask_EMA2'] - (0.1 * df['Ask_EMA2'])
        df['Ask_SMA3'] = talib.SMA(df['Ask_Close'], timeperiod=30)
        df['Ask_SMA3_Envelope_Upper'] = df['Ask_SMA3'] + (0.1 * df['Ask_SMA3'])
        df['Ask_SMA3_Envelope_Lower'] = df['Ask_SMA3'] - (0.1 * df['Ask_SMA3'])
        df['Ask_EMA3'] = talib.EMA(df['Ask_Close'], timeperiod=30)
        df['Ask_EMA3_Envelope_Upper'] = df['Ask_EMA3'] + (0.1 * df['Ask_EMA3'])
        df['Ask_EMA3_Envelope_Lower'] = df['Ask_EMA3'] - (0.1 * df['Ask_EMA3'])
        df['Ask_BB_Upper_Band'], df['Ask_BB_Middle_Band'], df['Ask_BB_Lower_Band'] = talib.BBANDS(
            df['Ask_Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        df['Ask_MACD'], df['Ask_MACD_Signal'], df['Ask_MACD_hist'] = talib.MACD(df['Ask_Close'],
                                                                                fastperiod=12,
                                                                                slowperiod=26,
                                                                                signalperiod=9)
        df['Ask_Parabollic_SAR'] = talib.SAR(df['Ask_High'], df['Ask_Low'], acceleration=0, maximum=0)
        df['Ask_Slowk'], df['Ask_Slowd'] = talib.STOCH(df['Ask_High'], df['Ask_Low'], df['Ask_Close'],
                                                       fastk_period=5, slowk_period=3,
                                                       slowk_matype=0, slowd_period=3,
                                                       slowd_matype=0)
        df['Ask_RSI'] = talib.RSI(df['Ask_Close'], timeperiod=14)
        df['Ask_Williams_Percent_Range'] = talib.WILLR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'],
                                                       timeperiod=14)
        df['Ask_ADX'] = talib.ADX(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)
        df['Ask_ADXR'] = talib.ADXR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)
        df['Ask_MOM'] = talib.MOM(df['Ask_Close'], timeperiod=10)
        df['Ask_BOP'] = talib.BOP(df['Ask_Open'], df['Ask_High'], df['Ask_Low'], df['Ask_Close'])
        df['Ask_AROONOSC'] = talib.AROONOSC(df['Ask_High'], df['Ask_Low'], timeperiod=14)
        df['Ask_ATR'] = talib.ATR(df['Ask_High'], df['Ask_Low'], df['Ask_Close'], timeperiod=14)

        dates = df['Date']
        df.drop('Date', axis=1, inplace=True)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        scaler_to_use = self.scalers[currency_pair]

        df = scaler_to_use.transform(df)

        print('Last date for current sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-1]))

        return df

    def format_macd_data(self, currency_pair, df):
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Bid_Close'])
        df['ema200'] = talib.EMA(df['Bid_Close'], timeperiod=200)

        dates = df['Date']
        df.drop('Date', axis=1, inplace=True)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        print('Second to last date for current macd sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-2]))
        print('Last date for current macd sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-1]))

        return df

    def format_kiss_data(self, currency_pair, df):
        df.Date = pd.to_datetime(df.Date, format='%Y.%m.%d %H:%M:%S.%f')

        df['ma5'] = talib.EMA(df['Bid_Close'], timeperiod=5)
        df['ma10'] = talib.EMA(df['Bid_Close'], timeperiod=10)
        df['slowk'], df['slowd'] = talib.STOCH(df['Bid_High'], df['Bid_Low'], df['Bid_Close'])
        df['rsi'] = talib.RSI(df['Bid_Close'], timeperiod=9)

        dates = df['Date']
        df.drop('Date', axis=1, inplace=True)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        print('Second to last date for current kiss sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-2]))
        print('Last date for current kiss sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-1]))

        return df

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
        dates = df.iloc[df.shape[0] - 100:, 0]
        df.drop('Date', axis=1, inplace=True)

        df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Mid_Close'])
        df['ema200'] = talib.EMA(df['Mid_Close'], timeperiod=200)
        df['ema50'] = talib.EMA(df['Mid_Close'], timeperiod=50)
        df = df.astype(float)

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[df.shape[0] - 100:, :]
        df.reset_index(drop=True, inplace=True)

        df['fractal'] = [self._add_fractal(df, i) for i in range(df.shape[0])]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df['beep_boop'] = [self._add_beep_boop(df, i) for i in range(df.shape[0])]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        print('Second to last date for current beep boop sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-2]))
        print('Last date for current beep boop sequence on ' + str(currency_pair) + ': ' + str(dates.iloc[-1]))

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
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = df.iloc[df.shape[0] - look_back_size:, :]
        df.dropna(inplace=True)
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
