import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
from Data.data_formatter import DataFormatter
import pytz as tz


class CurrentDataSequence:
    def __init__(self):
        self.beep_boop_current_sequences = {'GBP_USD': None}
        self.cnn_gasf_data = {'GBP_JPY': None}
        self.cnn_price_data = {'GBP_JPY': None}
        self.stoch_macd_current_sequences = {'GBP_USD': None}
        self.min_sequence_length = 1000
        self.data_formatter = DataFormatter()

    def update_beep_boop_current_data_sequence(self, currency_pair):
        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=0) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=4000))
        to_time = str(current_time)

        print('Data for beep boop on ' + str(currency_pair) + ':')

        data_downloader = DataDownloader()

        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask', 'mid'], 'H1', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c), float(candle.mid.o), float(candle.mid.h), float(candle.mid.l), float(candle.mid.c)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 1000:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_beep_boop_data(currency_pair, data_sequence)
        data_sequence.reset_index(drop=True, inplace=True)

        self.beep_boop_current_sequences[currency_pair] = data_sequence

        return True

    def update_cnn_current_data_sequence(self, currency_pair):
        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=0) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=4000))
        to_time = str(current_time)

        print('Data for cnn on ' + str(currency_pair) + ':')

        data_downloader = DataDownloader()

        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask', 'mid'], 'H1', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c), float(candle.mid.o), float(candle.mid.h), float(candle.mid.l), float(candle.mid.c)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 1000:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        gasf_data, price_data = self.data_formatter.format_cnn_data(currency_pair, data_sequence)

        self.cnn_gasf_data[currency_pair] = gasf_data
        self.cnn_price_data[currency_pair] = price_data

        return True

    def update_stoch_macd_current_data_sequence(self, currency_pair):
        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time.minute = current_time.minute - current_time.minute % 15
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=1000))
        to_time = str(current_time)

        print('Data for stoch macd on ' + str(currency_pair) + ':')

        data_downloader = DataDownloader()

        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask', 'mid'], 'M15', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c), float(candle.mid.o), float(candle.mid.h), float(candle.mid.l), float(candle.mid.c)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Mid_Open', 'Mid_High', 'Mid_Low', 'Mid_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 1000:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_stoch_macd_data(currency_pair, data_sequence)
        data_sequence.reset_index(drop=True, inplace=True)

        self.stoch_macd_current_sequences[currency_pair] = data_sequence

        return True

    def get_beep_boop_sequence_for_pair(self, currency_pair):
        return self.beep_boop_current_sequences[currency_pair]

    def get_cnn_sequence_for_pair(self, currency_pair):
        return self.cnn_gasf_data[currency_pair], self.cnn_price_data[currency_pair]

    def get_stoch_macd_sequence_for_pair(self, currency_pair):
        return self.stoch_macd_current_sequences[currency_pair]
