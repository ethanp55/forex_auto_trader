

class BeepBoop(object):
    def __init__(self, max_open_trades):
        self.max_open_trades = max_open_trades

    def predict(self, currency_pair, current_data, n_open_trades):
        beep_boop1 = current_data.loc[current_data.index[-1], 'beep_boop']
        beep_boop2 = current_data.loc[current_data.index[-2], 'beep_boop']
        beep_boop3 = current_data.loc[current_data.index[-3], 'beep_boop']
        beep_boop4 = current_data.loc[current_data.index[-4], 'beep_boop']
        ema200 = current_data.loc[current_data.index[-1], 'ema200']
        bid_low1 = current_data.loc[current_data.index[-1], 'Bid_Low']
        bid_high1 = current_data.loc[current_data.index[-1], 'Bid_High']
        bid_open1 = current_data.loc[current_data.index[-1], 'Bid_Open']
        bid_close1 = current_data.loc[current_data.index[-1], 'Bid_Close']

        print('New data for: ' + str(currency_pair))
        print('beep_boop1: ' + str(beep_boop1))
        print('beep_boop2: ' + str(beep_boop2))
        print('beep_boop3: ' + str(beep_boop3))
        print('beep_boop4: ' + str(beep_boop4))
        print('ema200: ' + str(ema200))
        print('bid_low1: ' + str(bid_low1))
        print('bid_high1: ' + str(bid_high1))
        print('bid_open1: ' + str(bid_open1))
        print('bid_close1: ' + str(bid_close1))
        print()

        if float(bid_low1) > float(ema200) and beep_boop4 == 1 and beep_boop3 == 1 and beep_boop2 == 1 and beep_boop1 == 1 and n_open_trades < self.max_open_trades and bid_open1 < bid_close1:
            trade = 'buy'

        elif float(bid_high1) < float(ema200) and beep_boop4 == 2 and beep_boop3 == 2 and beep_boop2 == 2 and beep_boop1 == 2 and n_open_trades < self.max_open_trades and bid_open1 > bid_close1:
            trade = 'sell'

        else:
            trade = None

        print('Beep boop trade: ' + str(trade))
        print('-------------------------------------------------------\n')

        return trade
