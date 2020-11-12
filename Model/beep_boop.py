

class BeepBoop(object):

    @staticmethod
    def predict(currency_pair, current_data):
        macdhist1 = current_data.loc[current_data.index[-1], 'macdhist']
        ema1 = current_data.loc[current_data.index[-1], 'ema']
        bid_low1 = current_data.loc[current_data.index[-1], 'Bid_Low']
        bid_high1 = current_data.loc[current_data.index[-1], 'Bid_High']

        print('\nNew data for: ' + str(currency_pair))
        print('macdhist1: ' + str(macdhist1))
        print('ema1: ' + str(ema1))
        print('bid_low1: ' + str(bid_low1))
        print('bid_high1: ' + str(bid_high1))
        print()

        if float(macdhist1) > 0 and float(bid_low1) > float(ema1):
            trade = 'buy'

        elif float(macdhist1) < 0 and float(bid_high1) < float(ema1):
            trade = 'sell'

        else:
            trade = None

        print('Beep boop trade: ' + str(trade))
        print('-------------------------------------------------------')

        return trade
