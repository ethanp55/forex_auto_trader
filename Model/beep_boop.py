

class BeepBoop(object):

    @staticmethod
    def predict(currency_pair, current_data):
        macdhist1 = current_data.loc[current_data.index[-1], 'macdhist']
        macdhist2 = current_data.loc[current_data.index[-2], 'macdhist']
        ema1 = current_data.loc[current_data.index[-1], 'ema']
        ema2 = current_data.loc[current_data.index[-2], 'ema']
        bid_low1 = current_data.loc[current_data.index[-1], 'Bid_Low']
        bid_low2 = current_data.loc[current_data.index[-2], 'Bid_Low']
        bid_high1 = current_data.loc[current_data.index[-1], 'Bid_High']
        bid_high2 = current_data.loc[current_data.index[-2], 'Bid_High']

        print('\nNew data for: ' + str(currency_pair))
        print('macdhist1: ' + str(macdhist1))
        print('macdhist2: ' + str(macdhist2))
        print('ema1: ' + str(ema1))
        print('ema2: ' + str(ema1))
        print('bid_low1: ' + str(bid_low1))
        print('bid_low2: ' + str(bid_low2))
        print('bid_high1: ' + str(bid_high1))
        print('bid_high2: ' + str(bid_high2))
        print()

        if float(macdhist1) > 0 and float(macdhist2) > 0 and float(bid_low1) > float(ema1) and float(bid_low2) > float(ema2):
            trade = 'buy'

        elif float(macdhist1) < 0 and float(macdhist2) < 0 and float(bid_high1) < float(ema1) and float(bid_high2) < float(ema2):
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('-------------------------------------------------------')

        return trade
