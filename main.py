from datetime import datetime, timedelta
import pytz as tz
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
from Model.beep_boop import BeepBoop
import traceback

weekend_day_nums = [4, 5, 6]
beep_boop_gain_risk_ratio = {'GBP_USD': 2}
beep_boop_pullback_cushion = {'GBP_USD': 0.0020}
max_open_trades = 10
beep_boop_n_units_per_trade = {'GBP_USD': 10000}
current_data_sequence = CurrentDataSequence()
data_downloader = DataDownloader()
open_beep_boop_pairs = {'GBP_USD': True}
open_trade_instruments = set()
beep_boop_model = BeepBoop(max_open_trades)
account_balance = 2000
percent_to_risk = 0.05
all_buys = False
all_sells = False
num_open_trades = 0


def _get_dt():
    utc_now = datetime.utcnow().replace(microsecond=0, second=0)

    if utc_now.weekday() in weekend_day_nums:
        if (utc_now.weekday() == 4 and utc_now.hour >= 20) or (
                utc_now.weekday() == 6 and utc_now.hour <= 21) or utc_now.weekday() == 5:
            print('Weekend hours, need to wait until market opens again.')

            while True:
                new_utc_now = datetime.utcnow().replace(microsecond=0, second=0)

                if new_utc_now.weekday() == 6 and new_utc_now.hour > 21:
                    break

    dt_h1 = datetime.strptime((datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, minute=0, second=0) + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    return dt_h1


def _get_open_trades(dt):
    try:
        global open_trade_instruments
        global open_beep_boop_pairs
        global all_buys
        global all_sells
        global num_open_trades

        all_buys = False
        all_sells = False
        num_open_trades = max_open_trades

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

        trade_types = []

        for order in open_trades:
            trade_types.append(order.currentUnits > 0)

        if len(trade_types) == 0:
            all_buys = True
            all_sells = True

        else:
            all_buys = all(trade_types)
            all_sells = not all_buys

        num_open_trades = len(open_trades)

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


def _calculate_pips_to_risk(current_data, trade_type, pullback_cushion, bid_open, ask_open):
    pullback = None
    i = current_data.shape[0] - 1

    if trade_type == 'buy':
        while i >= 0:
            curr_fractal = current_data.loc[current_data.index[i], 'fractal']

            if curr_fractal == 1:
                pullback = current_data.loc[current_data.index[i], 'Ask_Low']
                break

            i -= 1

    elif trade_type == 'sell':
        while i >= 0:
            curr_fractal = current_data.loc[current_data.index[i], 'fractal']

            if curr_fractal == 2:
                pullback = current_data.loc[current_data.index[i], 'Bid_High']
                break

            i -= 1

    if pullback is not None and trade_type == 'buy':
        stop_loss = round(pullback - pullback_cushion, 5)

        if stop_loss >= ask_open:
            return None

        pips_to_risk = ask_open - stop_loss

        return pips_to_risk

    elif pullback is not None and trade_type == 'sell':
        stop_loss = round(pullback + pullback_cushion, 5)

        if stop_loss <= bid_open:
            return None

        pips_to_risk = stop_loss - bid_open

        return pips_to_risk

    else:
        return None


def main():
    dt_h1 = _get_dt()

    open_trades_success = _get_open_trades(dt_h1)

    if not open_trades_success:
        main()

    for currency_pair in open_beep_boop_pairs:
        print('Starting new session with beep boop open for ' + str(currency_pair) + ': ' + str(open_beep_boop_pairs[currency_pair]))

    print('New session started with ' + str(num_open_trades) + ' open trades')

    while True:
        dt_h1 = _get_dt()

        error_flag = False

        print('\n---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print(dt_h1)
        print()

        open_trades_success = _get_open_trades(dt_h1)

        if not open_trades_success:
            continue

        print('Open trades: ' + str(num_open_trades))
        print('All buys: ' + str(all_buys))
        print('All sells: ' + str(all_sells) + '\n')

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------- BEEP BOOP --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        data_sequences = {}

        for currency_pair in open_beep_boop_pairs:
            if not open_beep_boop_pairs[currency_pair] or num_open_trades < max_open_trades:
                current_data_update_success = _update_beep_boop_current_data_sequence(dt_h1, currency_pair)

                if not current_data_update_success:
                    error_flag = True
                    break

                data_sequences[currency_pair] = current_data_sequence.get_beep_boop_sequence_for_pair(currency_pair)

        if error_flag:
            continue

        predictions = {}

        for currency_pair in data_sequences:
            pred = beep_boop_model.predict(currency_pair, data_sequences[currency_pair], num_open_trades)
            predictions[currency_pair] = pred

        for currency_pair in predictions:
            pred = predictions[currency_pair]

            if pred is not None:
                print('----------------------------------')
                print('-- PLACING NEW ORDER (BEEP BOOP) --')
                print('------------ ' + str(currency_pair) + ' -------------')
                print('----------------------------------\n')

                candles = _get_current_data(dt_h1, currency_pair, ['bid', 'ask'], 'H1')

                if candles is None:
                    error_flag = True
                    break

                last_candle = candles[-1]
                curr_bid_open = float(last_candle.bid.o)
                curr_ask_open = float(last_candle.ask.o)
                gain_risk_ratio = beep_boop_gain_risk_ratio[currency_pair]
                pips_to_risk = _calculate_pips_to_risk(data_sequences[currency_pair], pred, beep_boop_pullback_cushion[currency_pair], curr_bid_open, curr_ask_open)

                if pips_to_risk is not None and (pips_to_risk * 10000) / account_balance <= percent_to_risk:
                    n_units_per_trade = beep_boop_n_units_per_trade[currency_pair]

                    if pred == 'buy':
                        profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), 5)

                    else:
                        profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), 5)

                    print('Action: ' + str(pred) + ' for ' + str(currency_pair))
                    print('Profit price: ' + str(profit_price))
                    print()

                    order_placed = _place_market_order(dt_h1, currency_pair, pred, n_units_per_trade, profit_price,
                                                       pips_to_risk)

                    if not order_placed:
                        error_flag = True
                        break

        if error_flag:
            continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # Give Oanda a few seconds to process the trades
        time.sleep(15)

        open_trades_success = _get_open_trades(dt_h1)

        if not open_trades_success:
            continue

        for currency_pair in open_beep_boop_pairs:
            print('Open beep boop trade for ' + str(currency_pair) + ': ' + str(open_beep_boop_pairs[currency_pair]) + '\n')

        while datetime.strptime((datetime.now(tz=tz.timezone('America/New_York'))).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') < dt_h1:
            time.sleep(1)

        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')
        print('---------------------------------------------------------------------------------')


if __name__ == "__main__":
    main()
