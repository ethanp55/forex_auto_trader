from datetime import datetime
from Oanda.Services.data_downloader import DataDownloader


class TrainDataUpdater:
    def __init__(self):
        self.data_downloader = DataDownloader()

    def get_old_nfp_data(self):
        prev_nfp_date = datetime.strptime('2020-10-03 00:00:00', '%Y-%m-%d %H:%M:%S')
        return prev_nfp_date, 661000, 850000, 1489000

    def get_new_nfp_data(self):
        return 661000, 850000, 1489000
