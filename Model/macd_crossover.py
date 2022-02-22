import numpy as np


class MacdCrossover(object):

    @staticmethod
    def predict(current_data, current_data_long, curr_ask_open, curr_bid_open, spread_percentage):
        ema200_2, ema25_2, sar2, rsi2, mid_open2, mid_close2, mid_low2, mid_high2, vo2 = current_data.loc[current_data.index[-2], [
            'ema200', 'ema25', 'sar', 'rsi', 'Mid_Open', 'Mid_Close', 'Mid_Low', 'Mid_High', 'vo']]
        ema200_1, ema25_1, sar1, rsi1, mid_open1, mid_close1, mid_low1, mid_high1, vo1, ask_open1, ask_close1, bid_open1, bid_close1 = current_data.loc[current_data.index[-1], [
            'ema200', 'ema25', 'sar', 'rsi', 'Mid_Open', 'Mid_Close', 'Mid_Low', 'Mid_High', 'vo', 'Ask_Open', 'Ask_Close', 'Bid_Open', 'Bid_Close']]
        ema200_1_long, chop1_long = current_data_long.loc[current_data_long.index[-1], [
            'ema200', 'chop36']]
        macd2, macdsignal2, rsi2, rsi_sma2, chop2 = current_data.loc[current_data.index[-2], [
            'macd', 'macdsignal', 'rsi', 'rsi_sma', 'chop36']]
        macd1, macdsignal1, rsi1, rsi_sma1, chop1 = current_data.loc[current_data.index[-1], [
            'macd', 'macdsignal', 'rsi', 'rsi_sma', 'chop36']]
        spread = abs(curr_ask_open - curr_bid_open)
        macd_vals = [0, macd2, macdsignal2, macd1, macdsignal1]
        stoch_vals = list(
            current_data.loc[current_data.index[-12:], 'slowk_rsi'])
        stoch_vals_2 = list(
            current_data.loc[current_data.index[-12:], 'slowd_rsi'])
        emas_buy_signal = ema200_1 < mid_close1 and ema200_1_long < mid_close1 and ema200_1_long < ema200_1
        emas_sell_signal = ema200_1 > mid_close1 and ema200_1_long > mid_close1 and ema200_1_long > ema200_1

        sar_buy_signal = sar1 < min([mid_open1, mid_close1])
        sar_sell_signal = sar1 > max([mid_open1, mid_close1])

        rsi_buy_signal = rsi1 > rsi_sma1
        rsi_sell_signal = rsi1 < rsi_sma1

        macd_buy_signal = macd2 < macdsignal2 and macd1 > macdsignal1 and max(
            macd_vals) == 0
        macd_sell_signal = macd2 > macdsignal2 and macd1 < macdsignal1 and min(
            macd_vals) == 0

        stoch_buy_signal = False
        stoch_buy_changed = False
        stoch_sell_signal = False
        stoch_sell_changed = False

        # for i in range(len(stoch_vals) - 1, -1, -1):
        #     if stoch_vals[i] > 80 or stoch_vals_2[i] > 80 and not stoch_buy_changed:
        #         stoch_buy_signal = False
        #         stoch_buy_changed = True

        #     if stoch_vals[i] < 20 and stoch_vals_2[i] < 20 and not stoch_buy_changed:
        #         stoch_buy_signal = True
        #         stoch_buy_changed = True

        #     if stoch_vals[i] < 20 or stoch_vals_2[i] < 20 and not stoch_sell_changed:
        #         stoch_sell_signal = False
        #         stoch_sell_changed = True

        #     if stoch_vals[i] > 80 and stoch_vals_2[i] > 80 and not stoch_sell_changed:
        #         stoch_sell_signal = True
        #         stoch_sell_changed = True

        stoch_buy_signal = True
        stoch_sell_signal = True

        chop_signal = chop1_long < 0.50

        vo_signal = min([vo2, vo1]) > 0

        bullish_candle = mid_close1 > mid_open1
        bearish_candle = mid_close1 < mid_open1

        mid_highs = list(
            current_data.loc[current_data.index[-38:-2], 'Mid_High'])
        mid_lows = list(
            current_data.loc[current_data.index[-38:-2], 'Mid_Low'])
        differences = []

        for i in range(len(mid_highs)):
            differences.append(abs(mid_highs[i] - mid_lows[i]))

        mean, std = np.array(differences).mean(), np.array(differences).std()

        bars_small_enough = abs(mid_high1 - mid_low1) <= mean + \
            (std / 2) and abs(mid_high2 - mid_low2) <= mean + (std / 2)

        trade = None

        if macd_buy_signal and emas_buy_signal and sar_buy_signal and rsi_buy_signal and stoch_buy_signal and chop_signal and bullish_candle and bars_small_enough:
            pips_to_risk = curr_ask_open - sar1

            if spread <= pips_to_risk * spread_percentage:
                trade = 'buy'

        elif macd_sell_signal and emas_sell_signal and sar_sell_signal and rsi_sell_signal and stoch_sell_signal and chop_signal and bearish_candle and bars_small_enough:
            pips_to_risk = curr_bid_open + sar1

            if spread <= pips_to_risk * spread_percentage:
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
