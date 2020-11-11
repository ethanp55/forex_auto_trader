from datetime import datetime, timedelta
import pytz as tz
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
from Model.beep_boop import BeepBoop
import traceback

weekend_day_nums = [4, 5, 6]
time_frame_granularity = 4  # Hours
beep_boop_pips_to_risk = {'NZD_USD': 5 / 10000}
beep_boop_gain_risk_ratio = {'NZD_USD': 5}
n_units_per_trade = 200000
current_data_sequence = CurrentDataSequence()
data_downloader = DataDownloader()
open_beep_boop_pairs = {'NZD_USD': True}
open_trade_instruments = set()


def _get_dt():
    utc_now = datetime.utcnow().replace(microsecond=0, second=0)

    if utc_now.weekday() in weekend_day_nums:
        if (utc_now.weekday() == 4 and utc_now.hour >= 20) or (
                utc_now.weekday() == 6 and utc_now.hour <= 21) or utc_now.weekday() == 5:
            print('Weekend hours, need to wait until market opens again.')

            while True:
                new_utc_now = datetime.utcnow().replace(microsecond=0, second=0)

                if new_utc_now.weekday() == 6 and new_utc_now.hour > 20:
                    break

    dt = datetime.strptime((datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, minute=0, second=0) + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    return dt


def _get_open_trades(dt):
    try:
        global open_trade_instruments
        global open_beep_boop_pairs

        open_trade_instruments.clear()

        for currency_pair in open_beep_boop_pairs:
            open_beep_boop_pairs[currency_pair] = True

        open_trades, error_message = OrderHandler.get_open_trades()

        if error_message is not None:
            print(error_message)

            while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
                time.sleep(1)

            return False

        for order in open_trades:
            open_trade_instruments.add(order.instrument)

        for currency_pair in open_beep_boop_pairs:
            open_beep_boop_pairs[currency_pair] = currency_pair in open_trade_instruments

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


def _place_market_order(dt, currency_pair, pred, n_units_per_trade, profit_price, pips_to_risk):
    try:
        OrderHandler.place_market_order(currency_pair, pred, n_units_per_trade, profit_price, pips_to_risk)

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

    for currency_pair in open_beep_boop_pairs:
        print('Starting new session; session started with open ' + str(currency_pair) + ' beep boop trade: ' + str(open_beep_boop_pairs[currency_pair]))

    while True:
        dt = _get_dt()
        print('\n---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print(dt)

        open_trades_success = _get_open_trades(dt)

        if not open_trades_success:
            continue

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------- BEEP BOOP --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        data_sequences = {}

        for currency_pair in open_beep_boop_pairs:
            if not open_beep_boop_pairs[currency_pair]:
                current_data_update_success = _update_beep_boop_current_data_sequence(dt, currency_pair)

                if not current_data_update_success:
                    continue

                data_sequences[currency_pair] = current_data_sequence.get_beep_boop_sequence_for_pair(currency_pair)

        predictions = {}

        for currency_pair in data_sequences:
            pred = BeepBoop.predict(currency_pair, data_sequences[currency_pair])
            predictions[currency_pair] = pred

        for currency_pair in predictions:
            pred = predictions[currency_pair]

            if pred is not None:
                print('\n----------------------------------')
                print('---- PLACING NEW ORDER (MACD) ----')
                print('------------ ' + str(currency_pair) + ' -------------')
                print('----------------------------------\n')

                candles = _get_current_data(dt, currency_pair, ['bid', 'ask'], 'M30')

                if candles is None:
                    continue

                last_candle = candles[-1]
                curr_bid_open = float(last_candle.bid.o)
                curr_ask_open = float(last_candle.ask.o)
                gain_risk_ratio = beep_boop_gain_risk_ratio[currency_pair]
                pips_to_risk = beep_boop_pips_to_risk[currency_pair]

                if pred == 'buy':
                    profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), 5)

                else:
                    profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), 5)

                print('Action: ' + str(pred) + ' for ' + str(currency_pair))
                print('Profit price: ' + str(profit_price))
                print()

                order_placed = _place_market_order(dt, currency_pair, pred, n_units_per_trade, profit_price, pips_to_risk)

                if not order_placed:
                    continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # Give Oanda a few seconds to process the trades
        time.sleep(15)

        open_trades_success = _get_open_trades(dt)

        if not open_trades_success:
            continue

        for currency_pair in open_beep_boop_pairs:
            print('Open beep boop trade for ' + str(currency_pair) + ': ' + str(open_beep_boop_pairs[currency_pair]))

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt:
            time.sleep(1)

        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')


if __name__ == "__main__":
    main()
