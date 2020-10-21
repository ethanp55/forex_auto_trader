import numpy as np
from tensorflow.keras.models import load_model


class ForexRNN:
    def __init__(self, proba_threshold=0.6):
        self.eur_usd_rnn = load_model('Data/Files/eur_usd_rnn.h5')
        self.gbp_chf_rnn = load_model('Data/Files/gbp_chf_rnn.h5')
        self.proba_threshold = proba_threshold

    def predict(self, currency_pair, input_vector):
        rnn_to_use = self.eur_usd_rnn if currency_pair == 'EUR_USD' else self.gbp_chf_rnn

        if rnn_to_use == self.eur_usd_rnn:
            print('EUR USD RNN')

        else:
            print('GBP CHF RNN')

        rows, columns = input_vector.shape

        rnn_pred = rnn_to_use.predict(input_vector.reshape(1, rows, columns))
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
