from datetime import datetime, timedelta
from logging import error
import pytz as tz
import time
from Data.current_data_sequence import CurrentDataSequence
from Data.sendgrid_client import SendgridClient
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
# from Model.stochastic_crossover import StochasticCrossover
from Model.macd_crossover import MacdCrossover
# from Model.beep_boop import BeepBoop
# from AAT.aat import AAT
import traceback
import numpy as np

weekend_day_nums = [4, 5, 6]

macd_gain_risk_ratio = {'GBP_USD': 2, 'AUD_JPY': 2, 'USD_CAD': 2, 'AUD_USD': 2,
                        'USD_CHF': 2, 'GBP_JPY': 2, 'EUR_USD': 2, 'USD_JPY': 2, 'NZD_USD': 2, 'EUR_JPY': 2, 'NZD_JPY': 2, 'NZD_CHF': 2, 'EUR_GBP': 2}
macd_cutoffs = {'GBP_USD': 0.0004, 'AUD_JPY': 0.04, 'USD_CAD': 0.0004, 'AUD_USD': 0.0004,
                'USD_CHF': 0.0004, 'GBP_JPY': 0.04, 'EUR_USD': 0.0004, 'USD_JPY': 0.04, 'NZD_USD': 0.0004, 'EUR_JPY': 0.04, 'NZD_JPY': 0.04, 'NZD_CHF': 0.0004, 'EUR_GBP': 0.0004}
macd_max_spread = {'GBP_USD': 0.00025, 'AUD_JPY': 0.025, 'USD_CAD': 0.00025, 'AUD_USD': 0.00025,
                   'USD_CHF': 0.00025, 'GBP_JPY': 0.025, 'EUR_USD': 0.00025, 'USD_JPY': 0.025, 'NZD_USD': 0.00025, 'EUR_JPY': 0.025, 'NZD_JPY': 0.025, 'NZD_CHF': 0.00025, 'EUR_GBP': 0.00025}
macd_bar_length = {'GBP_USD': 0.0005, 'AUD_JPY': 0.05, 'USD_CAD': 0.0005, 'AUD_USD': 0.0005,
                   'USD_CHF': 0.0005, 'GBP_JPY': 0.05, 'EUR_USD': 0.0005, 'USD_JPY': 0.05, 'NZD_USD': 0.0005, 'EUR_JPY': 0.05, 'NZD_JPY': 0.05, 'NZD_CHF': 0.0005, 'EUR_GBP': 0.0005}
macd_pullback_cushion = {'GBP_USD': 0.0005, 'AUD_JPY': 0.05, 'USD_CAD': 0.0005, 'AUD_USD': 0.0005,
                         'USD_CHF': 0.0005, 'GBP_JPY': 0.05, 'EUR_USD': 0.0005, 'USD_JPY': 0.05, 'NZD_USD': 0.0005, 'EUR_JPY': 0.05, 'NZD_JPY': 0.05, 'NZD_CHF': 0.0005, 'EUR_GBP': 0.0005}
macd_fractal_distance = {'GBP_USD': 0.0015, 'AUD_JPY': 0.15, 'USD_CAD': 0.0015, 'AUD_USD': 0.0015,
                         'USD_CHF': 0.0015, 'GBP_JPY': 0.15, 'EUR_USD': 0.0015, 'USD_JPY': 0.15, 'NZD_USD': 0.0015, 'EUR_JPY': 0.15, 'NZD_JPY': 0.15, 'NZD_CHF': 0.0015, 'EUR_GBP': 0.0015}
macd_max_pips_to_risk = {'GBP_USD': 0.0030, 'AUD_JPY': 0.30, 'USD_CAD': 0.0030, 'AUD_USD': 0.0030,
                         'USD_CHF': 0.0030, 'GBP_JPY': 0.30, 'EUR_USD': 0.0030, 'USD_JPY': 0.30, 'NZD_USD': 0.0030, 'EUR_JPY': 0.30, 'NZD_JPY': 0.30, 'NZD_CHF': 0.0030, 'EUR_GBP': 0.0030}
macd_min_pips_to_risk = {'GBP_USD': 0.0010, 'AUD_JPY': 0.10, 'USD_CAD': 0.0010, 'AUD_USD': 0.0010,
                         'USD_CHF': 0.0010, 'GBP_JPY': 0.10, 'EUR_USD': 0.0010, 'USD_JPY': 0.10, 'NZD_USD': 0.0010, 'EUR_JPY': 0.10, 'NZD_JPY': 0.10, 'NZD_CHF': 0.0010, 'EUR_GBP': 0.0010}
macd_n_units_per_trade = {'GBP_USD': 50000, 'AUD_JPY': 50000, 'USD_CAD': 50000, 'AUD_USD': 50000,
                          'USD_CHF': 50000, 'GBP_JPY': 50000, 'EUR_USD': 50000, 'USD_JPY': 50000, 'NZD_USD': 50000, 'EUR_JPY': 50000, 'NZD_JPY': 50000, 'NZD_CHF': 50000, 'EUR_GBP': 50000}
macd_rounding = {'GBP_USD': 5, 'AUD_JPY': 3, 'USD_CAD': 5, 'AUD_USD': 5,
                 'USD_CHF': 5, 'GBP_JPY': 3, 'EUR_USD': 5, 'USD_JPY': 3, 'NZD_USD': 5, 'EUR_JPY': 3, 'NZD_JPY': 3, 'NZD_CHF': 5, 'EUR_GBP': 5}
macd_use_trailing_stop = {'GBP_USD': False, 'AUD_JPY': False, 'USD_CAD': False, 'AUD_USD': False,
                          'USD_CHF': False, 'GBP_JPY': False, 'EUR_USD': False, 'USD_JPY': False, 'NZD_USD': False, 'EUR_JPY': False, 'NZD_JPY': False, 'NZD_CHF': False, 'EUR_GBP': False}
macd_all_buys = {'GBP_USD': True, 'AUD_JPY': True, 'USD_CAD': True, 'AUD_USD': True,
                 'USD_CHF': True, 'GBP_JPY': True, 'EUR_USD': True, 'USD_JPY': True, 'NZD_USD': True, 'EUR_JPY': True, 'NZD_JPY': True, 'NZD_CHF': True, 'EUR_GBP': True}
macd_all_sells = {'GBP_USD': True, 'AUD_JPY': True, 'USD_CAD': True, 'AUD_USD': True,
                  'USD_CHF': True, 'GBP_JPY': True, 'EUR_USD': True, 'USD_JPY': True, 'NZD_USD': True, 'EUR_JPY': True, 'NZD_JPY': True, 'NZD_CHF': True, 'EUR_GBP': True}
macd_max_open_trades = {'GBP_USD': 1, 'AUD_JPY': 1, 'USD_CAD': 1, 'AUD_USD': 1,
                        'USD_CHF': 1, 'GBP_JPY': 1, 'EUR_USD': 1, 'USD_JPY': 1, 'NZD_USD': 1, 'EUR_JPY': 1, 'NZD_JPY': 1, 'NZD_CHF': 1, 'EUR_GBP': 1}
open_macd_pairs = {'GBP_USD': 0, 'USD_CAD': 0, 'AUD_USD': 0,
                   'USD_CHF': 0, 'EUR_USD': 0, 'USD_JPY': 0, 'NZD_USD': 0, 'EUR_GBP': 0}

# stoch_macd_gain_risk_ratio = {'GBP_USD': 1.8}
# stoch_macd_possible_pullback_cushions = {'GBP_USD': np.arange(39, 42)}
# stoch_macd_pullback_cushion = {'GBP_USD': 0.0040}
# stoch_macd_n_units_per_trade = {'GBP_USD': 50000}
# stoch_macd_rounding = {'GBP_USD': 5}
# stoch_macd_max_pips_to_risk = {'GBP_USD': 0.0100}
# stoch_macd_use_trailing_stop = {'GBP_USD': True}
# stoch_macd_all_buys = {'GBP_USD': True}
# stoch_macd_all_sells = {'GBP_USD': True}
# stoch_macd_max_open_trades = {'GBP_USD': 1}
# open_stoch_macd_pairs = {'GBP_USD': 0}
# stoch_signals = {'GBP_USD': None}
# stoch_possible_time_frames = {'GBP_USD': np.arange(10, 12)}
# stoch_time_frames = {'GBP_USD': 10}

# beep_boop_gain_risk_ratio = {'GBP_USD': 2}
# beep_boop_pullback_cushion = {'GBP_USD': 0.0010}
# beep_boop_adx_percentage = {'GBP_USD': 30}
# beep_boop_max_spread = {'GBP_USD': 0.0003}
# beep_boop_bar_length = {'GBP_USD': 0.0005}
# beep_boop_fractal_distance = {'GBP_USD': 0.0020}
# beep_boop_n_units_per_trade = {'GBP_USD': 50000}
# beep_boop_rounding = {'GBP_USD': 5}
# beep_boop_max_pips_to_risk = {'GBP_USD': 0.0100}
# beep_boop_use_trailing_stop = {'GBP_USD': True}
# beep_boop_all_buys = {'GBP_USD': True}
# beep_boop_all_sells = {'GBP_USD': True}
# beep_boop_max_open_trades = {'GBP_USD': 1}
# open_beep_boop_pairs = {'GBP_USD': 0}
# open_beep_boop_trades = {'GBP_USD': []}

current_data_sequence = CurrentDataSequence()
data_downloader = DataDownloader()
# aat_model = AAT()


def _get_dt():
    utc_now = datetime.utcnow().replace(microsecond=0, second=0)

    if utc_now.weekday() in weekend_day_nums:
        if (utc_now.weekday() == 4 and utc_now.hour > 20) or (
                utc_now.weekday() == 6 and utc_now.hour < 21) or utc_now.weekday() == 5:
            print('Weekend hours, need to wait until market opens again.')

            while True:
                new_utc_now = datetime.utcnow().replace(microsecond=0, second=0)

                if new_utc_now.weekday() == 6 and new_utc_now.hour >= 21:
                    break

    current_minutes = (datetime.now(tz=tz.timezone(
        'America/New_York')).replace(microsecond=0, second=0)).minute
    dt_m5 = datetime.strptime((datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0,
                               minute=current_minutes - current_minutes % 5) + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    return dt_m5


def _get_open_trades(dt):
    try:
        # global open_stoch_macd_pairs
        # global stoch_macd_all_buys
        # global stoch_macd_all_sells
        # global stoch_macd_n_units_per_trade

        # global open_beep_boop_pairs
        # global beep_boop_n_units_per_trade
        # global beep_boop_all_buys
        # global beep_boop_all_sells

        global open_macd_pairs
        global macd_n_units_per_trade
        global macd_all_buys
        global macd_all_sells

        for currency_pair in open_macd_pairs:
            open_macd_pairs[currency_pair] = 0
            macd_n_units_per_trade[currency_pair] = 50000
            macd_all_buys[currency_pair] = True
            macd_all_sells[currency_pair] = True

        open_trades, error_message = OrderHandler.get_open_trades()

        if error_message is not None:
            print(error_message)

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        for trade in open_trades:
            if trade.instrument in open_macd_pairs:
                # Increment the number of open trades for the given pair
                open_macd_pairs[trade.instrument] += 1

                # Increment the number of units (so that the next trade has a unique number of units in order to satisfy the
                # FIFO requirement)
                if abs(trade.currentUnits) >= macd_n_units_per_trade[trade.instrument]:
                    macd_n_units_per_trade[trade.instrument] = abs(
                        trade.currentUnits) + 1

                # Determine if all the trades for the pair are buys or sells
                if trade.currentUnits < 0 and macd_all_buys[trade.instrument]:
                    macd_all_buys[trade.instrument] = False

                if trade.currentUnits > 0 and macd_all_sells[trade.instrument]:
                    macd_all_sells[trade.instrument] = False

        return True

    except Exception as e:
        error_message = 'Error when trying to get open trades'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_beep_boop_current_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_beep_boop_current_data_sequence(
            currency_pair)

        if not current_data_update_success:
            print('Error updating beep boop data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + \
            str(currency_pair) + ' beep boop current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_beep_boop_aat_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_beep_boop_aat_data_sequence(
            currency_pair)

        if not current_data_update_success:
            print('Error updating beep boop data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + \
            str(currency_pair) + ' beep boop current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_cnn_current_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_cnn_current_data_sequence(
            currency_pair)

        if not current_data_update_success:
            print('Error updating cnn data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + \
            str(currency_pair) + ' cnn current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_stoch_macd_current_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_stoch_macd_current_data_sequence(
            currency_pair)

        if not current_data_update_success:
            print('Error updating stoch macd data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + \
            str(currency_pair) + ' stoch macd current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _get_current_data(dt, currency_pair, candle_types, time_granularity):
    try:
        candles, error_message = data_downloader.get_current_data(
            currency_pair, candle_types, time_granularity)

        if error_message is not None:
            print(error_message)

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return None

        return candles

    except Exception as e:
        error_message = 'Error when trying to get retrieve current market data'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return None


def _place_market_order(dt, currency_pair, pred, n_units_per_trade, profit_price, stop_loss, pips_to_risk, use_trailing_stop):
    try:
        OrderHandler.place_market_order(
            currency_pair, pred, n_units_per_trade, profit_price, stop_loss, pips_to_risk, use_trailing_stop)

        return True

    except Exception as e:
        error_message = 'Error when trying to place order'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _calculate_pips_to_risk(currency_pair, current_data, trade_type, pullback_cushion, bid_open, ask_open, atr, fractal_distance=0):
    stop_loss = None
    lowest_low = min(current_data.loc[current_data.index[len(
        current_data) - 12:], 'Mid_Low'])
    highest_high = max(
        current_data.loc[current_data.index[len(current_data) - 12:], 'Mid_High'])

    if trade_type == 'buy':
        stop_loss = lowest_low

        if ask_open - stop_loss > macd_max_pips_to_risk[currency_pair]:
            stop_loss = ask_open - macd_max_pips_to_risk[currency_pair]

        elif ask_open - stop_loss < macd_min_pips_to_risk[currency_pair]:
            stop_loss = ask_open - macd_min_pips_to_risk[currency_pair]

        pips_to_risk = ask_open - stop_loss

        return pips_to_risk, stop_loss

    else:
        stop_loss = highest_high

        if stop_loss - bid_open > macd_max_pips_to_risk[currency_pair]:
            stop_loss = bid_open + macd_max_pips_to_risk[currency_pair]

        elif stop_loss - bid_open < macd_min_pips_to_risk[currency_pair]:
            stop_loss = bid_open + macd_min_pips_to_risk[currency_pair]

        pips_to_risk = stop_loss - bid_open

        return pips_to_risk, stop_loss

    # ema200 = current_data.loc[current_data.index[-1], 'ema200']
    # ema175 = current_data.loc[current_data.index[-1], 'ema175']
    # ema150 = current_data.loc[current_data.index[-1], 'ema150']
    # ema125 = current_data.loc[current_data.index[-1], 'ema125']
    # ema100 = current_data.loc[current_data.index[-1], 'ema100']
    # ema75 = current_data.loc[current_data.index[-1], 'ema75']
    # reverse_flag = trade_type == 'buy'
    # ema_vals = sorted([ema75, ema100, ema125, ema150,
    #                   ema175, ema200], reverse=reverse_flag)

    # if trade_type == 'buy':
    #     for ema_val in ema_vals:
    #         if ema_val <= lowest_low:
    #             stop_loss = ema_val
    #             break

    #     if stop_loss is None:
    #         stop_loss = lowest_low

    #     pips_to_risk = ask_open - stop_loss

    #     return pips_to_risk, stop_loss

    # else:
    #     for ema_val in ema_vals:
    #         if ema_val >= highest_high:
    #             stop_loss = ema_val
    #             break

    #     if stop_loss is None:
    #         stop_loss = highest_high

    #     pips_to_risk = stop_loss - bid_open

    #     return pips_to_risk, stop_loss

    # pullback = None
    # i = current_data.shape[0] - 3

    # if trade_type == 'buy':
    #     while i >= 0:
    #         if current_data.loc[current_data.index[i], 'fractal'] == 1:
    #             curr_pullback = current_data.loc[current_data.index[i], 'Bid_Low']
    #             curr_fractal_distance = ask_open - curr_pullback

    #             if curr_fractal_distance >= fractal_distance:
    #                 pullback = curr_pullback
    #                 break

    #         i -= 1

    # elif trade_type == 'sell':
    #     while i >= 0:
    #         if current_data.loc[current_data.index[i], 'fractal'] == 2:
    #             curr_pullback = current_data.loc[current_data.index[i], 'Ask_High']
    #             curr_fractal_distance = curr_pullback - bid_open

    #             if curr_fractal_distance >= fractal_distance:
    #                 pullback = curr_pullback
    #                 break

    #         i -= 1

    # if pullback is not None and trade_type == 'buy':
    #     stop_loss = pullback - pullback_cushion

    #     if stop_loss >= ask_open:
    #         return None, None

    #     pips_to_risk = ask_open - stop_loss

    #     return pips_to_risk, stop_loss

    # elif pullback is not None and trade_type == 'sell':
    #     stop_loss = pullback + pullback_cushion

    #     if stop_loss <= bid_open:
    #         return None, None

    #     pips_to_risk = stop_loss - bid_open

    #     return pips_to_risk, stop_loss

    # else:
    #     return None, None


def _check_on_trades(dt_m5):
    open_trades, error_message = OrderHandler.get_open_trades()

    if error_message is not None:
        print(error_message)
        return

    for trade in open_trades:
        if trade.initialUnits == trade.currentUnits and trade.unrealizedPL > 0:
            currency_pair = trade.instrument

            while True:
                price_data, error_message = data_downloader.get_current_tick_data(
                    currency_pair)

                if error_message is None:
                    break

                else:
                    print(error_message)

                if datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') >= dt_m5:
                    return

            bid_price = price_data[0].bids[0].price
            ask_price = price_data[0].asks[0].price

            is_buy = trade.initialUnits > 0
            trade_open = trade.price
            trade_sl = trade.stopLossOrder.price
            pips_risked = trade_open - trade_sl if is_buy else trade_sl - trade_open
            pips_risked = round(
                pips_risked, macd_rounding[currency_pair])
            pips_gained = bid_price - trade_open if is_buy else trade_open - ask_price
            pips_gained = round(pips_gained, macd_rounding[currency_pair])

            if pips_gained >= pips_risked:
                while True:
                    update_error1 = OrderHandler.close_trade(
                        trade.id, int(trade.initialUnits / 2))

                    if update_error1 is None:
                        break

                    else:
                        print(update_error1)

                    if datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') >= dt_m5:
                        return

                while True:
                    update_error2 = OrderHandler.update_trade_stop_loss(
                        trade.id, round(trade_open, macd_rounding[currency_pair]))

                    if update_error2 is None:
                        break

                    else:
                        print(update_error2)

                    if datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') >= dt_m5:
                        return


def main():
    # global stoch_signals
    # global stoch_time_frames
    # global stoch_macd_pullback_cushion

    dt_m5 = _get_dt()

    open_trades_success = _get_open_trades(dt_m5)

    if not open_trades_success:
        main()

    for currency_pair in open_macd_pairs:
        print('Starting new session with macd open for ' +
              str(currency_pair) + ': ' + str(open_macd_pairs[currency_pair]))

    while True:
        dt_m5 = _get_dt()

        error_flag = False

        print('\n---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print(dt_m5)
        print()

        open_trades_success = _get_open_trades(dt_m5)

        if not open_trades_success:
            continue

        # --------------------------------------------------------------------------------------------------------------
        # ---------------------------------------------------- MACD ----------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        data_sequences = {}

        for currency_pair in open_macd_pairs:
            if open_macd_pairs[currency_pair] < macd_max_open_trades[currency_pair]:
                current_data_update_success = _update_stoch_macd_current_data_sequence(
                    dt_m5, currency_pair)

                if not current_data_update_success:
                    error_flag = True
                    break

                data_sequences[currency_pair] = current_data_sequence.get_stoch_macd_sequence_for_pair(
                    currency_pair)
                print()
                print(data_sequences[currency_pair])
                print()

        if error_flag:
            continue

        all_candles = {}

        for currency_pair in data_sequences:
            price_data, error_message = data_downloader.get_current_tick_data(
                currency_pair)

            if error_message is not None:
                print('Error getting current market data for: ' +
                      str(currency_pair))
                continue

            bid_price = price_data[0].bids[0].price
            ask_price = price_data[0].asks[0].price

            all_candles[currency_pair] = (float(bid_price), float(ask_price))

        predictions = {}

        for currency_pair in all_candles:
            curr_bid_open, curr_ask_open = all_candles[currency_pair]
            pred = MacdCrossover.predict(currency_pair, data_sequences[currency_pair], curr_ask_open,
                                         curr_bid_open, macd_cutoffs[currency_pair], macd_max_spread[currency_pair], macd_bar_length[currency_pair])
            predictions[currency_pair] = pred

        for currency_pair in predictions:
            pred = predictions[currency_pair]

            if pred is not None and ((pred == 'buy' and macd_all_buys[currency_pair]) or (pred == 'sell' and macd_all_sells[currency_pair])):
                SendgridClient.send_email(currency_pair, pred)
                # curr_bid_open, curr_ask_open = all_candles[currency_pair]
                # gain_risk_ratio = macd_gain_risk_ratio[currency_pair]
                # data_sequence = data_sequences[currency_pair]

                # pips_to_risk, stop_loss = _calculate_pips_to_risk(
                #     currency_pair, data_sequence, pred, macd_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open, data_sequence.loc[data_sequence.index[-1], 'atr'], macd_fractal_distance[currency_pair])

                # if stop_loss is not None and pips_to_risk <= macd_max_pips_to_risk[currency_pair]:
                #     print('----------------------------------')
                #     print('---- PLACING NEW ORDER (MACD) ----')
                #     print('------------ ' + str(currency_pair) + ' -------------')
                #     print('----------------------------------\n')

                #     n_units_per_trade = macd_n_units_per_trade[currency_pair]

                #     if pred == 'buy':
                #         profit_price = round(
                #             curr_ask_open + (gain_risk_ratio * pips_to_risk), macd_rounding[currency_pair])

                #     else:
                #         profit_price = round(
                #             curr_bid_open - (gain_risk_ratio * pips_to_risk), macd_rounding[currency_pair])

                #     print('Action: ' + str(pred) +
                #           ' for ' + str(currency_pair))
                #     print('Profit price: ' + str(profit_price))
                #     print('Stop loss price: ' + str(stop_loss))
                #     print('Pips to risk: ' + str(pips_to_risk))
                #     print('Rounded pips to risk: ' +
                #           str(round(pips_to_risk, macd_rounding[currency_pair])))
                #     print()

                #     order_placed = _place_market_order(dt_m5, currency_pair, pred, n_units_per_trade, profit_price,
                #                                        round(
                #                                            stop_loss, macd_rounding[currency_pair]),
                #                                        round(
                #                                            pips_to_risk, macd_rounding[currency_pair]),
                #                                        macd_use_trailing_stop[currency_pair])

                #     if not order_placed:
                #         error_flag = True
                #         break

                # else:
                #     print('Pips to risk is none or too high: ' + str(pips_to_risk))

        if error_flag:
            continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # # --------------------------------------------------------------------------------------------------------------
        # # ------------------------------------------------ STOCH MACD --------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------

        # data_sequences = {}

        # for currency_pair in open_stoch_macd_pairs:
        #     current_data_update_success = _update_stoch_macd_current_data_sequence(
        #         dt_m5, currency_pair)

        #     if not current_data_update_success:
        #         error_flag = True
        #         break

        #     data_sequences[currency_pair] = current_data_sequence.get_stoch_macd_sequence_for_pair(
        #         currency_pair)
        #     print()
        #     print(data_sequences[currency_pair])
        #     print()

        # if error_flag:
        #     continue

        # for currency_pair in stoch_signals:
        #     new_stoch_signal = StochasticCrossover.predict(
        #         currency_pair, data_sequences[currency_pair], stoch_time_frames[currency_pair])

        #     stoch_signals[currency_pair] = new_stoch_signal
        #     stoch_time_frames[currency_pair] = np.random.choice(
        #         stoch_possible_time_frames[currency_pair], p=[0.70, 0.30])

        # predictions = {}

        # for currency_pair in data_sequences:
        #     if open_stoch_macd_pairs[currency_pair] < stoch_macd_max_open_trades[currency_pair]:
        #         pred = MacdCrossover.predict(
        #             currency_pair, data_sequences[currency_pair], stoch_signals[currency_pair])
        #         predictions[currency_pair] = pred

        # for currency_pair in stoch_time_frames:
        #     print('Stoch signal for ' + str(currency_pair) +
        #           ': ' + str(stoch_signals[currency_pair]))
        #     print('Stoch time frame ' + str(currency_pair) +
        #           ': ' + str(stoch_time_frames[currency_pair]))
        #     print('-------------------------------------------------------\n')

        # for currency_pair in predictions:
        #     pred = predictions[currency_pair]

        #     if pred is not None and ((pred == 'buy' and stoch_macd_all_buys[currency_pair]) or (pred == 'sell' and stoch_macd_all_sells[currency_pair])):
        #         stoch_macd_pullback_cushion[currency_pair] = np.random.choice(
        #             stoch_macd_possible_pullback_cushions[currency_pair], p=[0.20, 0.60, 0.20]) / 10000
        #         print('Stoch pullback cushion for ' + str(currency_pair) +
        #               ': ' + str(stoch_macd_pullback_cushion[currency_pair]))

        #         most_recent_data = False

        #         while not most_recent_data:
        #             most_recent_data = True
        #             candles = _get_current_data(
        #                 dt_m5, currency_pair, ['bid', 'ask'], 'M30')

        #             if candles is None:
        #                 error_flag = True
        #                 break

        #             if candles[-1].complete:
        #                 print(
        #                     'The current market data is not available yet: ' + str(candles[-1].time))
        #                 most_recent_data = False

        #         if error_flag:
        #             break

        #         last_candle = candles[-1]
        #         curr_bid_open = float(last_candle.bid.o)
        #         curr_ask_open = float(last_candle.ask.o)
        #         gain_risk_ratio = stoch_macd_gain_risk_ratio[currency_pair]
        #         pips_to_risk, stop_loss = _calculate_pips_to_risk(
        #             data_sequences[currency_pair], pred, stoch_macd_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open)

        #         if pips_to_risk is not None and pips_to_risk <= stoch_macd_max_pips_to_risk[currency_pair]:
        #             stoch_signals[currency_pair] = None

        #             print('----------------------------------')
        #             print('-- PLACING NEW ORDER (STOCH MACD) --')
        #             print('------------ ' + str(currency_pair) + ' -------------')
        #             print('----------------------------------\n')

        #             n_units_per_trade = stoch_macd_n_units_per_trade[currency_pair]

        #             if pred == 'buy':
        #                 profit_price = round(
        #                     curr_ask_open + (gain_risk_ratio * pips_to_risk), stoch_macd_rounding[currency_pair])

        #             else:
        #                 profit_price = round(
        #                     curr_bid_open - (gain_risk_ratio * pips_to_risk), stoch_macd_rounding[currency_pair])

        #             print('Action: ' + str(pred) +
        #                   ' for ' + str(currency_pair))
        #             print('Profit price: ' + str(profit_price))
        #             print('Stop loss price: ' + str(stop_loss))
        #             print('Pips to risk: ' + str(pips_to_risk))
        #             print('Rounded pips to risk: ' + str(round(pips_to_risk,
        #                   stoch_macd_rounding[currency_pair])))
        #             print()

        #             order_placed = _place_market_order(dt_m5, currency_pair, pred, n_units_per_trade, profit_price,
        #                                                round(
        #                                                    stop_loss, stoch_macd_rounding[currency_pair]),
        #                                                round(
        #                                                    pips_to_risk, stoch_macd_rounding[currency_pair]),
        #                                                stoch_macd_use_trailing_stop[currency_pair])

        #             if not order_placed:
        #                 error_flag = True
        #                 break

        #         else:
        #             print('Pips to risk is none or too high: ' + str(pips_to_risk))

        # if error_flag:
        #     continue

        # # --------------------------------------------------------------------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------- BEEP BOOP --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # data_sequences = {}

        # for currency_pair in open_beep_boop_pairs:
        #     current_data_update_success = _update_beep_boop_current_data_sequence(
        #         dt_m15, currency_pair)

        #     if not current_data_update_success:
        #         error_flag = True
        #         break

        #     aat_data_update_succes = _update_beep_boop_aat_data_sequence(
        #         dt_m15, currency_pair)

        #     if not aat_data_update_succes:
        #         error_flag = True
        #         break

        #     beep_boop_data = current_data_sequence.get_beep_boop_sequence_for_pair(
        #         currency_pair)
        #     beep_boop_aat_data = current_data_sequence.get_beep_boop_aat_for_pair(
        #         currency_pair)
        #     open_trades = open_beep_boop_trades[currency_pair]

        #     for active_trade in open_trades:
        #         aat_success = aat_model.evaluate_trade(
        #             active_trade, beep_boop_aat_data, beep_boop_adx_percentage[currency_pair], beep_boop_gain_risk_ratio[currency_pair])

        #         if not aat_success:
        #             error_flag = True
        #             break

        #     if open_beep_boop_pairs[currency_pair] < beep_boop_max_open_trades[currency_pair]:
        #         data_sequences[currency_pair] = beep_boop_data
        #         print('Current data for ' + str(currency_pair) + ':')
        #         print(data_sequences[currency_pair])
        #         print()

        # if error_flag:
        #     continue

        # all_candles = {}

        # for currency_pair in data_sequences:
        #     most_recent_data = False

        #     while not most_recent_data:
        #         most_recent_data = True
        #         candles = _get_current_data(
        #             dt_m15, currency_pair, ['bid', 'ask'], 'M15')

        #         if candles is None:
        #             print('Error getting current market data for: ' +
        #                   str(currency_pair))
        #             error_flag = True
        #             break

        #         if candles[-1].complete:
        #             print(
        #                 'The current market data is not available yet: ' + str(candles[-1].time))
        #             most_recent_data = False

        #     if error_flag:
        #         break

        #     all_candles[currency_pair] = candles

        # if error_flag:
        #     continue

        # predictions = {}

        # for currency_pair in data_sequences:
        #     candles = all_candles[currency_pair]
        #     last_candle = candles[-1]
        #     curr_bid_open = float(last_candle.bid.o)
        #     curr_ask_open = float(last_candle.ask.o)
        #     pred = BeepBoop.predict(
        #         currency_pair, data_sequences[currency_pair], curr_ask_open, curr_bid_open, beep_boop_adx_percentage[currency_pair], beep_boop_bar_length[currency_pair], beep_boop_max_spread[currency_pair])
        #     predictions[currency_pair] = pred

        # for currency_pair in predictions:
        #     pred = predictions[currency_pair]

        #     if pred is not None and ((pred == 'buy' and beep_boop_all_buys[currency_pair]) or (pred == 'sell' and beep_boop_all_sells[currency_pair])):
        #         candles = all_candles[currency_pair]
        #         last_candle = candles[-1]
        #         curr_bid_open = float(last_candle.bid.o)
        #         curr_ask_open = float(last_candle.ask.o)
        #         gain_risk_ratio = beep_boop_gain_risk_ratio[currency_pair]
        #         pips_to_risk, stop_loss = _calculate_pips_to_risk(
        #             data_sequences[currency_pair], pred, beep_boop_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open, beep_boop_fractal_distance[currency_pair])

        #         if pips_to_risk is not None and pips_to_risk <= beep_boop_max_pips_to_risk[currency_pair]:
        #             print('----------------------------------')
        #             print('-- PLACING NEW ORDER (BEEP BOOP) --')
        #             print('------------ ' + str(currency_pair) + ' -------------')
        #             print('----------------------------------\n')

        #             n_units_per_trade = beep_boop_n_units_per_trade[currency_pair]

        #             if pred == 'buy':
        #                 profit_price = round(
        #                     curr_ask_open + (gain_risk_ratio * pips_to_risk), beep_boop_rounding[currency_pair])

        #             else:
        #                 profit_price = round(
        #                     curr_bid_open - (gain_risk_ratio * pips_to_risk), beep_boop_rounding[currency_pair])

        #             print('Action: ' + str(pred) +
        #                   ' for ' + str(currency_pair))
        #             print('Profit price: ' + str(profit_price))
        #             print('Stop loss price: ' + str(stop_loss))
        #             print('Pips to risk: ' + str(pips_to_risk))
        #             print('Rounded pips to risk: ' +
        #                   str(round(pips_to_risk, beep_boop_rounding[currency_pair])))
        #             print()

        #             order_placed = _place_market_order(dt_m15, currency_pair, pred, n_units_per_trade, profit_price,
        #                                                round(
        #                                                    stop_loss, beep_boop_rounding[currency_pair]),
        #                                                round(
        #                                                    pips_to_risk, beep_boop_rounding[currency_pair]),
        #                                                beep_boop_use_trailing_stop[currency_pair])

        #             if not order_placed:
        #                 error_flag = True
        #                 break

        #             else:
        #                 AAT.reset_curr_tuple()

        #         else:
        #             print('Pips to risk is none or too high: ' + str(pips_to_risk))

        # if error_flag:
        #     continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # Give Oanda a few seconds to process the trades
        time.sleep(5)

        open_trades_success = _get_open_trades(dt_m5)

        if not open_trades_success:
            continue

        for currency_pair in open_macd_pairs:
            print('Open beep boop trade for ' + str(currency_pair) +
                  ': ' + str(open_macd_pairs[currency_pair]) + '\n')

        for currency_pair in macd_all_buys:
            print('All buys for ' + str(currency_pair) +
                  ': ' + str(macd_all_buys[currency_pair]))

        for currency_pair in macd_all_sells:
            print('All sells for ' + str(currency_pair) +
                  ': ' + str(macd_all_sells[currency_pair]))

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt_m5:
            time.sleep(1)

        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')


if __name__ == "__main__":
    main()
