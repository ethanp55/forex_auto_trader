

class MacdCrossover(object):

    @staticmethod
    def predict(currency_pair, current_data, curr_ask_open, curr_bid_open, macd_cutoff, max_spread, max_bar_length):
        ema200_2, ema25_2, sar2, mid_open2, mid_close2, mid_low2, mid_high2 = current_data.loc[current_data.index[-2], [
            'ema200', 'ema25', 'sar', 'Mid_Open', 'Mid_Close', 'Mid_Low', 'Mid_High']]
        ema200_1, ema25_1, sar1, mid_open1, mid_close1, mid_low1, mid_high1 = current_data.loc[current_data.index[-1], [
            'ema200', 'ema25', 'sar', 'Mid_Open', 'Mid_Close', 'Mid_Low', 'Mid_High']]
        spread = abs(curr_ask_open - curr_bid_open)
        enough_volatility = spread <= max_spread
        macd2, macdsignal2 = current_data.loc[current_data.index[-2], [
            'macd', 'macdsignal']]
        macd1, macdsignal1 = current_data.loc[current_data.index[-1], [
            'macd', 'macdsignal']]
        macd_vals = [0, macd2, macdsignal2, macd1, macdsignal1]
        emas_buy_signal = ema200_2 < mid_low2 and ema200_1 < mid_low1
        emas_sell_signal = ema200_2 > mid_high2 and ema200_1 > mid_high1

        print('New macd data for: ' + str(currency_pair))
        print('macd1: ' + str(macd1))
        print('macdsignal1: ' + str(macdsignal1))
        print('macd2: ' + str(macd2))
        print('macdsignal2: ' + str(macdsignal2))
        print()

        trade = None

        if macd2 < macdsignal2 and macd1 > macdsignal1 and max(macd_vals) == 0 and emas_buy_signal and enough_volatility:
            trade = 'buy'

        elif macd2 > macdsignal2 and macd1 < macdsignal1 and min(macd_vals) == 0 and emas_sell_signal and enough_volatility:
            trade = 'sell'

        print('Trade: ' + str(trade))
        print('-------------------------------------------------------\n')

        return trade

    @staticmethod
    def predict_with_stoch(currency_pair, current_data, stoch_signal):
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
