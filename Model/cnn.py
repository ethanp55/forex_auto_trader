import numpy as np
from tensorflow.keras.models import load_model


class ForexCNN:
    def __init__(self, proba_threshold=0.95):
        gbp_jpy_cnn = load_model('Model/Files/gbp_jpy_cnn.h5')
        self.cnns = {'GBP_JPY': gbp_jpy_cnn}
        self.proba_threshold = proba_threshold

    def predict(self, currency_pair, input_vector):
        cnn_to_use = self.cnns[currency_pair]

        rows, cols, channels = input_vector.shape

        cnn_pred = cnn_to_use.predict(input_vector.reshape(1, rows, cols, channels))
        cnn_pred_argmax = np.argmax(cnn_pred)
        cnn_pred_proba = cnn_pred[0][cnn_pred_argmax]

        print('CNN for ' + str(currency_pair) + ' --------------------------------------')
        print(cnn_pred)
        print(cnn_pred_argmax)
        print(cnn_pred_proba)

        if cnn_pred_argmax == 1 and cnn_pred_proba >= self.proba_threshold:
            trade = 'buy'

        elif cnn_pred_argmax == 2 and cnn_pred_proba >= self.proba_threshold:
            trade = 'sell'

        else:
            trade = None

        print(trade)
        print('-------------------------------------------------------')

        return trade
