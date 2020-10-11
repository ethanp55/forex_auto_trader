import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
from Data.data_formatter import DataFormatter
import pytz as tz


class CurrentDataSequence:
    def __init__(self):
        self.current_sequence = None
        self.min_sequence_length = 1000
        self.data_formatter = DataFormatter()

    def update_current_data_sequence(self, nfp_actual, nfp_forecast, nfp_previous):
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
            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c), float(nfp_actual), float(nfp_forecast), float(nfp_previous)]
            np_data.append(row)

        np_data = np.array(np_data)

        print('Last date for current sequence: ' + str(np_data[-1, 0]))

        self.current_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'Nonfarm_Payroll_Actual', 'Nonfarm_Payroll_Forecast', 'Nonfarm_Payroll_Previous'])
        self.current_sequence.dropna(inplace=True)
        self.current_sequence.reset_index(drop=True, inplace=True)

        if self.current_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(self.current_sequence.shape[0]))
            return False

        self.current_sequence = self.data_formatter.format_data(self.current_sequence)
        self.current_sequence = self.current_sequence[self.current_sequence.shape[0] - 60:, :]

        return True
