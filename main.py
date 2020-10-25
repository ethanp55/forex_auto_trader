from datetime import datetime, timedelta
import pytz as tz
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
from Data.train_data_updater import TrainDataUpdater
from Model.rnn import ForexRNN
import traceback

weekend_day_nums = [4, 5, 6]
time_frame_granularity = 30  # Minutes
pips_to_risk = 50 / 10000
n_units_per_trade = 10000
gain_risk_ratio = 2
current_data_sequence = CurrentDataSequence()
order_handler = OrderHandler(pips_to_risk)
data_downloader = DataDownloader()
train_data_updater = TrainDataUpdater()
forex_rnn = ForexRNN()
open_pairs = {'EUR_USD': False, 'GBP_CHF': False, 'USD_CAD': False}
open_trade_instruments = set()


def _get_dt():
    utc_now = datetime.utcnow().replace(microsecond=0, second=0)

    minutes = 0 if utc_now.minute < 30 else 30

    if utc_now.weekday() in weekend_day_nums:
        if (utc_now.weekday() == 4 and utc_now.hour >= 20) or (
                utc_now.weekday() == 6 and utc_now.hour <= 21) or utc_now.weekday() == 5:
            print('Weekend hours, need to wait until market opens again.')

            while True:
                new_utc_now = datetime.utcnow().replace(microsecond=0, second=0)

                if new_utc_now.weekday() == 6 and new_utc_now.hour > 20:
                    break

    dt = datetime.strptime((datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, minute=minutes, second=0) + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    return dt


def _get_open_trades(dt):
    try:
        global open_trade_instruments
        global open_pairs

        open_trade_instruments.clear()

        for currency_pair in open_pairs:
            open_pairs[currency_pair] = True

        open_trades, error_message = order_handler.get_open_trades()

        if error_message is not None:
            print(error_message)

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        for order in open_trades:
            open_trade_instruments.add(order.instrument)

        for currency_pair in open_pairs:
            open_pairs[currency_pair] = currency_pair in open_trade_instruments

        return True

    except Exception as e:
        error_message = 'Error when trying to get open trades'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_major_pair_current_data_sequence(dt, currency_pair, nfp_actual, nfp_forecast, nfp_previous, prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous):
    try:
        current_data_update_success = current_data_sequence.update_major_pair_current_data_sequence(currency_pair, nfp_actual, nfp_forecast,
                                                                                                    nfp_previous, prev_nfp_date,
                                                                                                    prev_nfp_actual,
                                                                                                    prev_nfp_forecast,
                                                                                                    prev_nfp_previous)

        if not current_data_update_success:
            print('Error updating ' + str(currency_pair) + ' data')

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update ' + str(currency_pair) + ' current data sequence'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def _update_gbp_chf_current_data_sequence(dt):
    try:
        current_data_update_success = current_data_sequence.update_gbp_chf_current_data_sequence()

        if not current_data_update_success:
            print('Error updating GBP/CHF data')

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        return True

    except Exception as e:
        error_message = 'Error when trying to get update GBP/CHF current data sequence'

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


def _place_market_order(dt, currency_pair, pred, n_units_per_trade, profit_price):
    try:
        order_handler.place_market_order(currency_pair, pred, n_units_per_trade, profit_price)

        return True

    except Exception as e:
        error_message = 'Error when trying to place order'

        print(error_message)
        print(e)
        print(traceback.print_exc())

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        return False


def main():
    dt = _get_dt()

    open_trades_success = _get_open_trades(dt)

    if not open_trades_success:
        main()

    for currency_pair in open_pairs:
        print('Starting new session; session started with open ' + str(currency_pair) + ' trade: ' + str(open_pairs[currency_pair]))

    while True:
        dt = _get_dt()
        print('\n---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print(dt)

        open_trades_success = _get_open_trades(dt)

        if not open_trades_success:
            continue

        data_sequences = {}

        for currency_pair in open_pairs:
            if not open_pairs[currency_pair]:
                if currency_pair == 'GBP_CHF':
                    current_data_update_success = _update_gbp_chf_current_data_sequence(dt)

                    if not current_data_update_success:
                        continue

                else:
                    prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous = train_data_updater.get_old_nfp_data()
                    nfp_actual, nfp_forecast, nfp_previous = train_data_updater.get_new_nfp_data()

                    current_data_update_success = _update_major_pair_current_data_sequence(dt, currency_pair, nfp_actual, nfp_forecast,
                                                                                           nfp_previous, prev_nfp_date,
                                                                                           prev_nfp_actual,
                                                                                           prev_nfp_forecast,
                                                                                           prev_nfp_previous)

                    if not current_data_update_success:
                        continue

                data_sequences[currency_pair] = current_data_sequence.get_sequence_for_pair(currency_pair)

        predictions = {}

        for currency_pair in data_sequences:
            pred = forex_rnn.predict(currency_pair, data_sequences[currency_pair])
            predictions[currency_pair] = pred

        time.sleep(1)

        for currency_pair in predictions:
            pred = predictions[currency_pair]

            if pred is not None:
                print('\n---------------------------------')
                print('------- PLACING NEW ORDER -------')
                print('------------ ' + str(currency_pair) + ' ------------')
                print('---------------------------------\n')

                candles = _get_current_data(dt, currency_pair, ['bid', 'ask'], 'M30')

                if candles is None:
                    continue

                last_candle = candles[-1]
                curr_bid_open = float(last_candle.bid.o)
                curr_ask_open = float(last_candle.ask.o)

                if pred == 'buy':
                    profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), 5)

                else:
                    profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), 5)

                print('Action: ' + str(pred) + ' for ' + str(currency_pair))
                print('Profit price: ' + str(profit_price))
                print()

                order_placed = _place_market_order(dt, currency_pair, pred, n_units_per_trade, profit_price)

                if not order_placed:
                    continue

        # Give Oanda a few seconds to process the trades
        time.sleep(15)

        open_trades_success = _get_open_trades(dt)

        if not open_trades_success:
            continue

        for currency_pair in open_pairs:
            print('Open trade for ' + str(currency_pair) + ': ' + str(open_pairs[currency_pair]))

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')


if __name__ == "__main__":
    main()
