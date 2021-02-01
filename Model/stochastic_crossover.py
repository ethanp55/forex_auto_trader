

class StochasticCrossover(object):

    @staticmethod
    def predict(currency_pair, current_data):
        slowk1 = current_data.loc[current_data.index[-1], 'slowk']
        slowd1 = current_data.loc[current_data.index[-1], 'slowd']
        slowk2 = current_data.loc[current_data.index[-2], 'slowk']
        slowd2 = current_data.loc[current_data.index[-2], 'slowd']

        print('New stochastic data for: ' + str(currency_pair))
        print('slowk1: ' + str(slowk1))
        print('slowd1: ' + str(slowd1))
        print('slowk2: ' + str(slowk2))
        print('slowd2: ' + str(slowd2))
        print()

        if slowk2 < slowd2 and slowk1 > slowd1 and max([20, slowk2, slowd2, slowk1, slowd1]) == 20:
            stoch_signal = 'buy'

        elif slowk2 > slowd2 and slowk1 < slowd1 and min([80, slowk2, slowd2, slowk1, slowd1]) == 80:
            stoch_signal = 'sell'

        else:
            stoch_signal = None

        print('Stoch signal: ' + str(stoch_signal))
        print('-------------------------------------------------------\n')

        return stoch_signal
