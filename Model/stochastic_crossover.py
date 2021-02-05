

class StochasticCrossover(object):

    @staticmethod
    def predict(currency_pair, current_data, time_window):
        stoch_signal = None

        for i in range(current_data.shape[0] - time_window, current_data.shape[0]):
            slowk1 = current_data.loc[current_data.index[i], 'slowk']
            slowd1 = current_data.loc[current_data.index[i], 'slowd']
            slowk2 = current_data.loc[current_data.index[i - 1], 'slowk']
            slowd2 = current_data.loc[current_data.index[i - 1], 'slowd']

            if slowk2 < slowd2 and slowk1 > slowd1 and max([20, slowk2, slowd2, slowk1, slowd1]) == 20:
                stoch_signal = 'buy'

            elif slowk2 > slowd2 and slowk1 < slowd1 and min([80, slowk2, slowd2, slowk1, slowd1]) == 80:
                stoch_signal = 'sell'

        return stoch_signal
