import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
from Data.data_formatter import DataFormatter
import pytz as tz


class CurrentDataSequence:
    def __init__(self):
        self.current_sequences = {'EUR_USD': None, 'GBP_CHF': None, 'USD_CAD': None, 'AUD_USD': None}
        self.macd_current_sequences = {'EUR_USD': None, 'GBP_USD': None}
        self.kiss_current_sequences = {'AUD_USD': None}
        self.beep_boop_current_sequences = {'GBP_USD': None, 'EUR_JPY': None, 'GBP_JPY': None}
        self.min_sequence_length = 1000
        self.data_formatter = DataFormatter()

    def update_gbp_chf_current_data_sequence(self):
        curr_date = datetime.now(tz=tz.timezone('America/New_York'))
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        # if dston <= curr_date.replace(tzinfo=None) < dstoff:
        #     hours = 2
        #
        # else:
        #     hours = 1

        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=minutes) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=40 * 24))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data('GBP_CHF', ['bid', 'ask'], 'M30', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')

            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_data('GBP_CHF', data_sequence)
        data_sequence = data_sequence[data_sequence.shape[0] - 60:, :]

        self.current_sequences['GBP_CHF'] = data_sequence

        return True

    def update_major_pair_current_data_sequence(self, currency_pair, nfp_actual, nfp_forecast, nfp_previous, prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous):
        curr_date = datetime.now(tz=tz.timezone('America/New_York'))
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        # if dston <= curr_date.replace(tzinfo=None) < dstoff:
        #     hours = 2
        #
        # else:
        #     hours = 1

        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=minutes) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=40 * 24))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask'], 'M30', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
            curr_date_datetime = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')

            if curr_date_datetime < prev_nfp_date:
                nfp_actual_to_use = prev_nfp_actual
                nfp_forecast_to_use = prev_nfp_forecast
                nfp_previous_to_use = prev_nfp_previous

            else:
                nfp_actual_to_use = nfp_actual
                nfp_forecast_to_use = nfp_forecast
                nfp_previous_to_use = nfp_previous

            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c), float(nfp_actual_to_use), float(nfp_forecast_to_use), float(nfp_previous_to_use)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Nonfarm_Payroll_Actual', 'Nonfarm_Payroll_Forecast', 'Nonfarm_Payroll_Previous'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_data(currency_pair, data_sequence)
        data_sequence = data_sequence[data_sequence.shape[0] - 60:, :]

        self.current_sequences[currency_pair] = data_sequence

        return True

    def update_macd_crossover_current_data_sequence(self, currency_pair):
        curr_date = datetime.now(tz=tz.timezone('America/New_York'))
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        # if dston <= curr_date.replace(tzinfo=None) < dstoff:
        #     hours = 2
        #
        # else:
        #     hours = 1

        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=minutes) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=40 * 48))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask'], 'M30', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')

            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c)]
            np_data.append(row)

        if currency_pair == 'GBP_USD':
            utc_now = datetime.utcnow().replace(microsecond=0, second=0, minute=minutes)
            utc_now = utc_now.strftime('%Y-%m-%d %H:%M:%S')
            utc_now = datetime.strptime(utc_now, '%Y-%m-%d %H:%M:%S')

            while True:
                candles, error_message = data_downloader.get_current_data('GBP_USD', ['bid', 'ask'], 'M30')

                if error_message is not None:
                    print(error_message)
                    return False

                curr_candle = candles[-1]
                curr_date = curr_candle.time
                curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
                curr_date_datetime = datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')

                if curr_date_datetime >= utc_now:
                    row = [curr_date, float(curr_candle.bid.o), float(curr_candle.bid.h), float(curr_candle.bid.l),
                           float(curr_candle.bid.c),
                           float(curr_candle.ask.o), float(curr_candle.ask.h), float(curr_candle.ask.l),
                           float(curr_candle.ask.c)]
                    np_data.append(row)

                    break

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 500:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_macd_data(currency_pair, data_sequence)
        data_sequence = data_sequence.iloc[data_sequence.shape[0] - 60:, :]
        data_sequence.reset_index(drop=True, inplace=True)

        self.macd_current_sequences[currency_pair] = data_sequence

        return True

    def update_kiss_current_data_sequence(self, currency_pair):
        curr_date = datetime.now(tz=tz.timezone('America/New_York'))
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        # if dston <= curr_date.replace(tzinfo=None) < dstoff:
        #     hours = 2
        #
        # else:
        #     hours = 1

        hours = 2

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=minutes) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=40 * 48))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data(currency_pair, ['bid', 'ask'], 'M30', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')

            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c)]
            np_data.append(row)

        np_data = np.array(np_data)

        data_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'])
        data_sequence.dropna(inplace=True)
        data_sequence.reset_index(drop=True, inplace=True)

        if data_sequence.shape[0] < 500:
            print('Current sequence length is too small: ' + str(data_sequence.shape[0]))
            return False

        data_sequence = self.data_formatter.format_kiss_data(currency_pair, data_sequence)
        data_sequence = data_sequence.iloc[data_sequence.shape[0] - 60:, :]
        data_sequence.reset_index(drop=True, inplace=True)

        self.kiss_current_sequences[currency_pair] = data_sequence

        return True

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

    def get_sequence_for_pair(self, currency_pair):
        return self.current_sequences[currency_pair]

    def get_macd_sequence_for_pair(self, currency_pair):
        return self.macd_current_sequences[currency_pair]

    def get_kiss_sequence_for_pair(self, currency_pair):
        return self.kiss_current_sequences[currency_pair]

    def get_beep_boop_sequence_for_pair(self, currency_pair):
        return self.beep_boop_current_sequences[currency_pair]
