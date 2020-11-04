from collections import deque


class KISS(object):

    @staticmethod
    def predict(currency_pair, current_data):
        ma_val_buffer = 3
        slowk_vals = deque(maxlen=ma_val_buffer)
        slowd_vals = deque(maxlen=ma_val_buffer)

        for i in range(current_data.shape[0] - ma_val_buffer, current_data.shape[0]):
            slowk, slowd = current_data.loc[current_data.index[i], ['slowk', 'slowd']]
            slowk_vals.append(slowk)
            slowd_vals.append(slowd)

        prev_ma5, prev_ma10 = current_data.loc[current_data.index[-2], ['ma5', 'ma10']]

        bid_open, bid_high, bid_low, bid_close, ask_open, ask_high, ask_low, ask_close, slowk, slowd, rsi, ma5, ma10 = current_data.loc[current_data.index[-1], ['Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close', 'slowk', 'slowd', 'rsi', 'ma5', 'ma10']]

        slowk_vals_list = list(slowk_vals)
        slowd_vals_list = list(slowd_vals)

        print('\nNew data for: ' + str(currency_pair))
        print('Prev MA5: ' + str(prev_ma5))
        print('Prev MA10: ' + str(prev_ma10))
        print('Curr MA5: ' + str(ma5))
        print('Curr MA10: ' + str(ma10))
        print('Curr RSI: ' + str(rsi))
        print('Curr slowk vals: ' + str(slowk_vals))
        print('Curr slowk: ' + str(slowk))
        print('Curr slowd vals: ' + str(slowd_vals))
        print('Curr slowd: ' + str(slowd))
        print()

        if all(i < j for i, j in zip(slowk_vals_list, slowk_vals_list[1:])) and all(i < j for i, j in zip(slowd_vals_list, slowd_vals_list[1:])) and slowk < 80 and slowd < 80 and rsi > 50 and prev_ma5 < prev_ma10 and ma5 > ma10:
            trade = 'buy'

        elif all(i > j for i, j in zip(slowk_vals_list, slowk_vals_list[1:])) and all(i > j for i, j in zip(slowd_vals_list, slowd_vals_list[1:])) and slowk > 20 and slowd > 20 and rsi < 50 and prev_ma5 > prev_ma10 and ma5 < ma10:
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('-------------------------------------------------------')

        return trade
