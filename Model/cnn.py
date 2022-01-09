from tensorflow.keras.models import load_model
from TimeSeries.gaf import GramianAngularField
import numpy as np


model = load_model('Model/files/forex_macd_cnn')
look_back_size = 200

labels = {0: 'No trade', 1: 'Buy', 2: 'Sell'}


class CNN(object):

    def _grab_image_data(subset):
        gasf_transformer = GramianAngularField(method='summation')
        gasf_subset = gasf_transformer.transform(subset)

        return gasf_subset

    @staticmethod
    def predict(current_data, curr_ask_open, curr_bid_open, max_spread):
        model_data = current_data.drop(['Date', 'Bid_Open', 'Bid_High', 'Bid_Low',
                                       'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'], axis=1)
        ema200_2, ema100_2, ema50_2, mid_low2, mid_high2 = current_data.loc[current_data.index[-2], [
            'ema200', 'ema100', 'ema50', 'Mid_Low', 'Mid_High']]
        ema200_1, ema100_1, ema50_1, mid_low1, mid_high1 = current_data.loc[current_data.index[-1], [
            'ema200', 'ema100', 'ema50', 'Mid_Low', 'Mid_High']]
        spread = abs(curr_ask_open - curr_bid_open)
        enough_volatility = spread <= max_spread
        macd2, macdsignal2 = current_data.loc[current_data.index[-2], [
            'macd', 'macdsignal']]
        macd1, macdsignal1 = current_data.loc[current_data.index[-1], [
            'macd', 'macdsignal']]
        macd_vals = [0, macd2, macdsignal2, macd1, macdsignal1]
        emas_buy_signal = ema200_2 < ema100_2 and ema200_1 < ema100_1 and ema100_2 < ema50_2 and ema100_1 < ema50_1
        emas_sell_signal = ema200_2 > ema100_2 and ema200_1 > ema100_1 and ema100_2 > ema50_2 and ema100_1 > ema50_1

        trade = None

        if macd2 < macdsignal2 and macd1 > macdsignal1 and max(macd_vals) == 0 and emas_buy_signal and enough_volatility:
            trade = 'buy'

        elif macd2 > macdsignal2 and macd1 < macdsignal1 and min(macd_vals) == 0 and emas_sell_signal and enough_volatility:
            trade = 'sell'

        if trade is not None:
            curr_seq = model_data.iloc[-look_back_size:, :]
            curr_seq = CNN._grab_image_data(curr_seq)

            pred = model.predict(curr_seq.reshape(
                1, curr_seq.shape[0], curr_seq.shape[1], curr_seq.shape[2]))

            pred_formatted = []
            probs = list(pred[0])

            for i in range(len(probs)):
                num = probs[i]
                pred_formatted.append(labels[i] + ' = ' + str(round(num, 5)))

            return trade, pred_formatted

        return None, None
