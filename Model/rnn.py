import numpy as np
from tensorflow.keras.models import load_model


class EurUsdRNN:
    def __init__(self):
        self.eur_usd_rnn = load_model('Model/Files/rnn.h5')

    def predict(self, input_vector):
        rows, columns = input_vector.shape
        rnn_pred = self.eur_usd_rnn.predict(input_vector.reshape(1, rows, columns))
        rnn_pred_argmax = np.argmax(rnn_pred)
        print('RNN --------------------------------------')
        print(rnn_pred)
        print(rnn_pred_argmax)

        if rnn_pred_argmax == 1:
            trade = 'buy'

        elif rnn_pred_argmax == 2:
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('------------------------------------------')

        return trade
