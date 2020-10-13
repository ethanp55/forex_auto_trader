import numpy as np
from tensorflow.keras.models import load_model


class EurUsdRNN:
    def __init__(self, proba_threshold=0.6):
        self.eur_usd_rnn = load_model('Model/Files/rnn.h5')
        self.proba_threshold = proba_threshold

    def predict(self, input_vector):
        rows, columns = input_vector.shape
        rnn_pred = self.eur_usd_rnn.predict(input_vector.reshape(1, rows, columns))
        rnn_pred_argmax = np.argmax(rnn_pred)
        rnn_pred_proba = rnn_pred[0][rnn_pred_argmax]
        print('RNN --------------------------------------')
        print(rnn_pred)
        print(rnn_pred_argmax)
        print(rnn_pred_proba)

        if rnn_pred_argmax == 1 and rnn_pred_proba >= self.proba_threshold:
            trade = 'buy'

        elif rnn_pred_argmax == 2 and rnn_pred_proba >= self.proba_threshold:
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('------------------------------------------')

        return trade
