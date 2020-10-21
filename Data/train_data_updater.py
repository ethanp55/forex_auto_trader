import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
import pytz as tz


class TrainDataUpdater:
    def __init__(self):
        self.data_downloader = DataDownloader()
        self.train_data = pd.read_csv('Data/Files/Oanda_Eur_Usd_M30_expanded.csv')
        self.train_data.Date = pd.to_datetime(self.train_data.Date)
        self.train_data.dropna(inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)

    def get_old_nfp_data(self):
        prev_nfp_date = datetime.strptime('2020-10-03 00:00:00', '%Y-%m-%d %H:%M:%S')
        return prev_nfp_date, 661000, 850000, 1489000

    def get_new_nfp_data(self):
        return 661000, 850000, 1489000

    def update_train_data(self):
        previous_date = self.train_data.loc[self.train_data.index[-1], 'Date']

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

        from_time = current_time - timedelta(hours=35 * 24)

        from_time = str(from_time)
        to_time = str(current_time)

        nfp_actual, nfp_forecast, nfp_previous = self.get_new_nfp_data()

        candles, error_message = self.data_downloader.get_historical_data('EUR_USD', ['bid', 'ask'], 'M30', from_time,
                                                                          to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []
        new_data_len = 0

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')

            if datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S').timestamp() <= previous_date.timestamp():
                continue

            else:
                new_data_len += 1

            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c),
                   float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c),
                   float(nfp_actual), float(nfp_forecast), float(nfp_previous)]
            np_data.append(row)

        np_data = np.array(np_data)
        new_data = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close',
                                                  'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close',
                                                  'Nonfarm_Payroll_Actual', 'Nonfarm_Payroll_Forecast',
                                                  'Nonfarm_Payroll_Previous'])

        self.train_data = self.train_data.append(new_data)
        self.train_data.dropna(inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)

        self.train_data = self.train_data.iloc[new_data_len:, :]
        self.train_data.dropna(inplace=True)
        self.train_data.reset_index(drop=True, inplace=True)

        self.train_data.to_csv('Data/Files/Oanda_Eur_Usd_M30_expanded_test.csv', index=False)

        return True
