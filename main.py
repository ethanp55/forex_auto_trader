from datetime import datetime, timedelta
import pytz as tz
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
# from Model.stochastic_crossover import StochasticCrossover
# from Model.macd_crossover import MacdCrossover
from Model.beep_boop import BeepBoop
import traceback
import numpy as np

weekend_day_nums = [4, 5, 6]

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

beep_boop_gain_risk_ratio = {'GBP_USD': 1.7}
beep_boop_pullback_cushion = {'GBP_USD': 0.0040}
beep_boop_n_units_per_trade = {'GBP_USD': 1000}
beep_boop_rounding = {'GBP_USD': 5}
beep_boop_max_pips_to_risk = {'GBP_USD': 0.0100}
beep_boop_use_trailing_stop = {'GBP_USD': True}
beep_boop_all_buys = {'GBP_USD': True}
beep_boop_all_sells = {'GBP_USD': True}
beep_boop_max_open_trades = {'GBP_USD': 1}
open_beep_boop_pairs = {'GBP_USD': 0}

current_data_sequence = CurrentDataSequence()
data_downloader = DataDownloader()


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

    current_minutes = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0)).minute
    dt_m5 = datetime.strptime((datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=current_minutes - current_minutes % 5) + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    return dt_m5


def _get_open_trades(dt):
    try:
        # global open_stoch_macd_pairs
        # global stoch_macd_all_buys
        # global stoch_macd_all_sells
        # global stoch_macd_n_units_per_trade
        global open_beep_boop_pairs
        global beep_boop_n_units_per_trade
        global beep_boop_all_buys
        global beep_boop_all_sells

        for currency_pair in open_beep_boop_pairs:
            open_beep_boop_pairs[currency_pair] = 0
            beep_boop_n_units_per_trade[currency_pair] = 1000
            beep_boop_all_buys[currency_pair] = True
            beep_boop_all_sells[currency_pair] = True

        open_trades, error_message = OrderHandler.get_open_trades()

        if error_message is not None:
            print(error_message)

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        for trade in open_trades:
            if trade.instrument in open_beep_boop_pairs:
                # Increment the number of open trades for the given pair
                open_beep_boop_pairs[trade.instrument] += 1

                # Increment the number of units (so that the next trade has a unique number of units in order to satisfy the
                # FIFO requirement)
                if abs(trade.currentUnits) >= beep_boop_n_units_per_trade[trade.instrument]:
                    beep_boop_n_units_per_trade[trade.instrument] = abs(trade.currentUnits) + 1

                # Determine if all the trades for the pair are buys or sells
                if trade.currentUnits < 0 and beep_boop_all_buys[trade.instrument]:
                    beep_boop_all_buys[trade.instrument] = False

                if trade.currentUnits > 0 and beep_boop_all_sells[trade.instrument]:
                    beep_boop_all_sells[trade.instrument] = False

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
        current_data_update_success = current_data_sequence.update_beep_boop_current_data_sequence(currency_pair)

        if not current_data_update_success:
            print('Error updating beep boop data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + str(currency_pair) + ' beep boop current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_cnn_current_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_cnn_current_data_sequence(currency_pair)

        if not current_data_update_success:
            print('Error updating cnn data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + str(currency_pair) + ' cnn current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_stoch_macd_current_data_sequence(dt, currency_pair):
    try:
        current_data_update_success = current_data_sequence.update_stoch_macd_current_data_sequence(currency_pair)

        if not current_data_update_success:
            print('Error updating stoch macd data for ' + str(currency_pair))

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + str(currency_pair) + ' stoch macd current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _get_current_data(dt, currency_pair, candle_types, time_granularity):
    try:
        candles, error_message = data_downloader.get_current_data(currency_pair, candle_types, time_granularity)

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
        OrderHandler.place_market_order(currency_pair, pred, n_units_per_trade, profit_price, stop_loss, pips_to_risk, use_trailing_stop)

        return True

    except Exception as e:
        error_message = 'Error when trying to place order'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _calculate_pips_to_risk(current_data, trade_type, pullback_cushion, bid_open, ask_open):
    pullback = None
    i = current_data.shape[0] - 4

    if trade_type == 'buy':
        while i >= 0:
            curr_fractal = current_data.loc[current_data.index[i], 'fractal']

            if curr_fractal == 1:
                pullback = current_data.loc[current_data.index[i], 'Bid_Low']
                break

            i -= 1

    elif trade_type == 'sell':
        while i >= 0:
            curr_fractal = current_data.loc[current_data.index[i], 'fractal']

            if curr_fractal == 2:
                pullback = current_data.loc[current_data.index[i], 'Ask_High']
                break

            i -= 1

    if pullback is not None and trade_type == 'buy':
        stop_loss = pullback - pullback_cushion

        if stop_loss >= ask_open:
            return None, None

        pips_to_risk = ask_open - stop_loss

        return pips_to_risk, stop_loss

    elif pullback is not None and trade_type == 'sell':
        stop_loss = pullback + pullback_cushion

        if stop_loss <= bid_open:
            return None, None

        pips_to_risk = stop_loss - bid_open

        return pips_to_risk, stop_loss

    else:
        return None, None


def main():
    # global stoch_signals
    # global stoch_time_frames
    # global stoch_macd_pullback_cushion

    dt_m5 = _get_dt()

    open_trades_success = _get_open_trades(dt_m5)

    if not open_trades_success:
        main()

    for currency_pair in open_beep_boop_pairs:
        print('Starting new session with beep boop open for ' + str(currency_pair) + ': ' + str(open_beep_boop_pairs[currency_pair]))

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

        # # --------------------------------------------------------------------------------------------------------------
        # # ------------------------------------------------ STOCH MACD --------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------
        #
        # data_sequences = {}
        #
        # for currency_pair in open_stoch_macd_pairs:
        #     current_data_update_success = _update_stoch_macd_current_data_sequence(dt_m5, currency_pair)
        #
        #     if not current_data_update_success:
        #         error_flag = True
        #         break
        #
        #     data_sequences[currency_pair] = current_data_sequence.get_stoch_macd_sequence_for_pair(currency_pair)
        #     print()
        #     print(data_sequences[currency_pair])
        #     print()
        #
        # if error_flag:
        #     continue
        #
        # for currency_pair in stoch_signals:
        #     new_stoch_signal = StochasticCrossover.predict(currency_pair, data_sequences[currency_pair], stoch_time_frames[currency_pair])
        #
        #     stoch_signals[currency_pair] = new_stoch_signal
        #     stoch_time_frames[currency_pair] = np.random.choice(stoch_possible_time_frames[currency_pair], p=[0.70, 0.30])
        #
        # predictions = {}
        #
        # for currency_pair in data_sequences:
        #     if open_stoch_macd_pairs[currency_pair] < stoch_macd_max_open_trades[currency_pair]:
        #         pred = MacdCrossover.predict(currency_pair, data_sequences[currency_pair], stoch_signals[currency_pair])
        #         predictions[currency_pair] = pred
        #
        # for currency_pair in stoch_time_frames:
        #     print('Stoch signal for ' + str(currency_pair) + ': ' + str(stoch_signals[currency_pair]))
        #     print('Stoch time frame ' + str(currency_pair) + ': ' + str(stoch_time_frames[currency_pair]))
        #     print('-------------------------------------------------------\n')
        #
        # for currency_pair in predictions:
        #     pred = predictions[currency_pair]
        #
        #     if pred is not None and ((pred == 'buy' and stoch_macd_all_buys[currency_pair]) or (pred == 'sell' and stoch_macd_all_sells[currency_pair])):
        #         stoch_macd_pullback_cushion[currency_pair] = np.random.choice(stoch_macd_possible_pullback_cushions[currency_pair], p=[0.20, 0.60, 0.20]) / 10000
        #         print('Stoch pullback cushion for ' + str(currency_pair) + ': ' + str(stoch_macd_pullback_cushion[currency_pair]))
        #
        #         most_recent_data = False
        #
        #         while not most_recent_data:
        #             most_recent_data = True
        #             candles = _get_current_data(dt_m5, currency_pair, ['bid', 'ask'], 'M30')
        #
        #             if candles is None:
        #                 error_flag = True
        #                 break
        #
        #             if candles[-1].complete:
        #                 print('The current market data is not available yet: ' + str(candles[-1].time))
        #                 most_recent_data = False
        #
        #         if error_flag:
        #             break
        #
        #         last_candle = candles[-1]
        #         curr_bid_open = float(last_candle.bid.o)
        #         curr_ask_open = float(last_candle.ask.o)
        #         gain_risk_ratio = stoch_macd_gain_risk_ratio[currency_pair]
        #         pips_to_risk, stop_loss = _calculate_pips_to_risk(data_sequences[currency_pair], pred, stoch_macd_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open)
        #
        #         if pips_to_risk is not None and pips_to_risk <= stoch_macd_max_pips_to_risk[currency_pair]:
        #             stoch_signals[currency_pair] = None
        #
        #             print('----------------------------------')
        #             print('-- PLACING NEW ORDER (STOCH MACD) --')
        #             print('------------ ' + str(currency_pair) + ' -------------')
        #             print('----------------------------------\n')
        #
        #             n_units_per_trade = stoch_macd_n_units_per_trade[currency_pair]
        #
        #             if pred == 'buy':
        #                 profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), stoch_macd_rounding[currency_pair])
        #
        #             else:
        #                 profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), stoch_macd_rounding[currency_pair])
        #
        #             print('Action: ' + str(pred) + ' for ' + str(currency_pair))
        #             print('Profit price: ' + str(profit_price))
        #             print('Stop loss price: ' + str(stop_loss))
        #             print('Pips to risk: ' + str(pips_to_risk))
        #             print('Rounded pips to risk: ' + str(round(pips_to_risk, stoch_macd_rounding[currency_pair])))
        #             print()
        #
        #             order_placed = _place_market_order(dt_m5, currency_pair, pred, n_units_per_trade, profit_price,
        #                                                round(stop_loss, stoch_macd_rounding[currency_pair]),
        #                                                round(pips_to_risk, stoch_macd_rounding[currency_pair]),
        #                                                stoch_macd_use_trailing_stop[currency_pair])
        #
        #             if not order_placed:
        #                 error_flag = True
        #                 break
        #
        #         else:
        #             print('Pips to risk is none or too high: ' + str(pips_to_risk))
        #
        # if error_flag:
        #     continue
        #
        # # --------------------------------------------------------------------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------
        # # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------- BEEP BOOP --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        data_sequences = {}

        for currency_pair in open_beep_boop_pairs:
            if open_beep_boop_pairs[currency_pair] < beep_boop_max_open_trades[currency_pair]:
                current_data_update_success = _update_beep_boop_current_data_sequence(dt_m5, currency_pair)

                if not current_data_update_success:
                    error_flag = True
                    break

                data_sequences[currency_pair] = current_data_sequence.get_beep_boop_sequence_for_pair(currency_pair)
                print('Current data for ' + str(currency_pair) + ':')
                print(data_sequences[currency_pair])
                print()

        if error_flag:
            continue

        all_candles = {}

        for currency_pair in data_sequences:
            most_recent_data = False

            while not most_recent_data:
                most_recent_data = True
                candles = _get_current_data(dt_m5, currency_pair, ['bid', 'ask'], 'M5')

                if candles is None:
                    print('Error getting current market data for: ' + str(currency_pair))
                    error_flag = True
                    break

                if candles[-1].complete:
                    print('The current market data is not available yet: ' + str(candles[-1].time))
                    most_recent_data = False

            if error_flag:
                break

            all_candles[currency_pair] = candles

        if error_flag:
            continue

        predictions = {}

        for currency_pair in data_sequences:
            candles = all_candles[currency_pair]
            last_candle = candles[-1]
            curr_bid_open = float(last_candle.bid.o)
            curr_ask_open = float(last_candle.ask.o)
            pred = BeepBoop.predict(currency_pair, data_sequences[currency_pair], curr_ask_open, curr_bid_open)
            predictions[currency_pair] = pred

        for currency_pair in predictions:
            pred = predictions[currency_pair]

            if pred is not None and ((pred == 'buy' and beep_boop_all_buys[currency_pair]) or (pred == 'sell' and beep_boop_all_sells[currency_pair])):
                candles = all_candles[currency_pair]
                last_candle = candles[-1]
                curr_bid_open = float(last_candle.bid.o)
                curr_ask_open = float(last_candle.ask.o)
                gain_risk_ratio = beep_boop_gain_risk_ratio[currency_pair]
                pips_to_risk, stop_loss = _calculate_pips_to_risk(data_sequences[currency_pair], pred, beep_boop_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open)

                if pips_to_risk is not None and pips_to_risk <= beep_boop_max_pips_to_risk[currency_pair]:
                    print('----------------------------------')
                    print('-- PLACING NEW ORDER (BEEP BOOP) --')
                    print('------------ ' + str(currency_pair) + ' -------------')
                    print('----------------------------------\n')

                    n_units_per_trade = beep_boop_n_units_per_trade[currency_pair]

                    if pred == 'buy':
                        profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), beep_boop_rounding[currency_pair])

                    else:
                        profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), beep_boop_rounding[currency_pair])

                    print('Action: ' + str(pred) + ' for ' + str(currency_pair))
                    print('Profit price: ' + str(profit_price))
                    print('Stop loss price: ' + str(stop_loss))
                    print('Pips to risk: ' + str(pips_to_risk))
                    print('Rounded pips to risk: ' + str(round(pips_to_risk, beep_boop_rounding[currency_pair])))
                    print()

                    order_placed = _place_market_order(dt_m5, currency_pair, pred, n_units_per_trade, profit_price,
                                                       round(stop_loss, beep_boop_rounding[currency_pair]),
                                                       round(pips_to_risk, beep_boop_rounding[currency_pair]),
                                                       beep_boop_use_trailing_stop[currency_pair])

                    if not order_placed:
                        error_flag = True
                        break

                else:
                    print('Pips to risk is none or too high: ' + str(pips_to_risk))

        if error_flag:
            continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # Give Oanda a few seconds to process the trades
        time.sleep(15)

        open_trades_success = _get_open_trades(dt_m5)

        if not open_trades_success:
            continue

        for currency_pair in open_beep_boop_pairs:
            print('Open beep boop trade for ' + str(currency_pair) + ': ' + str(open_beep_boop_pairs[currency_pair]) + '\n')

        for currency_pair in beep_boop_all_buys:
            print('All buys for ' + str(currency_pair) + ': ' + str(beep_boop_all_buys[currency_pair]))

        for currency_pair in beep_boop_all_sells:
            print('All sells for ' + str(currency_pair) + ': ' + str(beep_boop_all_sells[currency_pair]))

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt_m5:
            time.sleep(1)

        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')


if __name__ == "__main__":
    main()
