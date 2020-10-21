import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
from Data.data_formatter import DataFormatter
import pytz as tz


class CurrentDataSequence:
    def __init__(self):
        self.eur_usd_current_sequence = None
        self.gbp_chf_current_sequence = None
        self.min_sequence_length = 1000
        self.data_formatter = DataFormatter()

    def update_gbp_chf_current_data_sequence(self):
        curr_date = datetime.now()
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        if dston <= curr_date.replace(tzinfo=None) < dstoff:
            hours = 2

        else:
            hours = 1

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

        self.gbp_chf_current_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'])
        self.gbp_chf_current_sequence.dropna(inplace=True)
        self.gbp_chf_current_sequence.reset_index(drop=True, inplace=True)

        if self.gbp_chf_current_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(self.gbp_chf_current_sequence.shape[0]))
            return False

        self.gbp_chf_current_sequence = self.data_formatter.format_data('GBP_CHF', self.gbp_chf_current_sequence)
        self.gbp_chf_current_sequence = self.gbp_chf_current_sequence[self.gbp_chf_current_sequence.shape[0] - 60:, :]

        return True

    def update_eur_usd_current_data_sequence(self, nfp_actual, nfp_forecast, nfp_previous, prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous):
        curr_date = datetime.now()
        minutes = 0 if curr_date.minute < 30 else 30
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        if dston <= curr_date.replace(tzinfo=None) < dstoff:
            hours = 2

        else:
            hours = 1

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=minutes) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=40 * 24))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data('EUR_USD', ['bid', 'ask'], 'M30', from_time, to_time)

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

        self.eur_usd_current_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Nonfarm_Payroll_Actual', 'Nonfarm_Payroll_Forecast', 'Nonfarm_Payroll_Previous'])
        self.eur_usd_current_sequence.dropna(inplace=True)
        self.eur_usd_current_sequence.reset_index(drop=True, inplace=True)

        if self.eur_usd_current_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(self.eur_usd_current_sequence.shape[0]))
            return False

        self.eur_usd_current_sequence = self.data_formatter.format_data('EUR_USD', self.eur_usd_current_sequence)
        self.eur_usd_current_sequence = self.eur_usd_current_sequence[self.eur_usd_current_sequence.shape[0] - 60:, :]

        return True
