

class MACDCrossover(object):

    @staticmethod
    def predict(currency_pair, current_data):
        prev_macd, prev_macdsignal = current_data.loc[current_data.index[-2], ['macd', 'macdsignal']]
        curr_bid_open, curr_bid_high, curr_bid_low, curr_bid_close, curr_ask_open, curr_ask_high, curr_ask_low, curr_ask_close, curr_macd, curr_macdsignal, curr_macdhist, curr_ema200 = current_data.loc[current_data.index[-1], ['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'macd', 'macdsignal', 'macdhist', 'ema200']]

        print('\nNew data for: ' + str(currency_pair))
        print('Prev MACD: ' + str(prev_macd))
        print('Prev MACD signal: ' + str(prev_macdsignal))
        print('Curr MACD: ' + str(curr_macd))
        print('Curr MACD signal: ' + str(curr_macdsignal))
        print('Curr bid open: ' + str(curr_bid_open))
        print('Curr EMA 200: ' + str(curr_ema200))
        print()

        if float(prev_macd) < float(prev_macdsignal) and float(curr_macd) > float(curr_macdsignal) and min(float(curr_bid_low), float(curr_ema200)) == float(curr_ema200):
            trade = 'buy'

        elif float(prev_macd) > float(prev_macdsignal) and float(curr_macd) < float(curr_macdsignal) and max(float(curr_bid_high), float(curr_ema200)) == float(curr_ema200):
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('-------------------------------------------------------')

        return trade
