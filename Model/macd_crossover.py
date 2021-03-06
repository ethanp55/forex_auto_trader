

class MacdCrossover(object):

    @staticmethod
    def predict(currency_pair, current_data, stoch_signal):
        macd1 = current_data.loc[current_data.index[-1], 'macd']
        macdsignal1 = current_data.loc[current_data.index[-1], 'macdsignal']
        macd2 = current_data.loc[current_data.index[-2], 'macd']
        macdsignal2 = current_data.loc[current_data.index[-2], 'macdsignal']
        ema200 = current_data.loc[current_data.index[-1], 'ema200']
        bid_low1 = current_data.loc[current_data.index[-1], 'Mid_Low']
        bid_high1 = current_data.loc[current_data.index[-1], 'Mid_High']

        print('New macd data for: ' + str(currency_pair))
        print('macd1: ' + str(macd1))
        print('macdsignal1: ' + str(macdsignal1))
        print('macd2: ' + str(macd2))
        print('macdsignal2: ' + str(macdsignal2))
        print('ema200: ' + str(ema200))
        print('bid_low1: ' + str(bid_low1))
        print('bid_high1: ' + str(bid_high1))
        print()

        if macd2 < macdsignal2 and macd1 > macdsignal1 and bid_low1 > ema200 and stoch_signal == 'buy':
            trade = 'buy'

        elif macd2 > macdsignal2 and macd1 < macdsignal1 and bid_high1 < ema200 and stoch_signal == 'sell':
            trade = 'sell'

        else:
            trade = None

        print('Trade: ' + str(trade))
        print('-------------------------------------------------------\n')

        return trade
