from datetime import datetime, timedelta
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
from Data.train_data_updater import TrainDataUpdater
from Model.rnn import EurUsdRNN


def main():
    weekend_day_nums = [4, 5, 6]
    pips_to_risk = 50 / 10000
    n_units_per_trade = 10000
    gain_risk_ratio = 2
    current_data_sequence = CurrentDataSequence()
    order_handler = OrderHandler(pips_to_risk)
    data_downloader = DataDownloader()
    train_data_updater = TrainDataUpdater()
    eur_usd_rnn = EurUsdRNN()

    open_trades, error_message = order_handler.get_open_trades()

    if error_message is not None:
        print('Error in getting open trades:\n' + error_message)
        return

    else:
        order_in_place = len(open_trades) > 0

    print('Starting new session; session started with open trades: ' + str(order_in_place))

    while True:
        utc_now = datetime.utcnow().replace(microsecond=0, second=0)

        minutes = 0 if utc_now.minute < 30 else 30

        if utc_now.weekday() in weekend_day_nums:
            if (utc_now.weekday() == 4 and utc_now.hour >= 20) or (utc_now.weekday() == 6 and utc_now.hour <= 21) or utc_now.weekday() == 5:
                print('Weekend hours, need to wait until market opens again.')

                while True:
                    new_utc_now = datetime.utcnow().replace(microsecond=0, second=0)

                    if new_utc_now.weekday() == 6 and new_utc_now.hour > 20:
                        break

        dt = datetime.now().replace(microsecond=0, minute=minutes, second=0) + timedelta(minutes=30)
        print(dt)

        if not order_in_place:
            prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous = train_data_updater.get_old_nfp_data()
            nfp_actual, nfp_forecast, nfp_previous = train_data_updater.get_new_nfp_data()

            current_data_update_success = current_data_sequence.update_current_data_sequence(nfp_actual, nfp_forecast, nfp_previous, prev_nfp_date, prev_nfp_actual, prev_nfp_forecast, prev_nfp_previous)

            if not current_data_update_success:
                print('Error in current data sequence')
                return

            data_sequence = current_data_sequence.current_sequence

            pred = eur_usd_rnn.predict(data_sequence)

            if pred is not None:
                print('\n---------------------------------')
                print('------- PLACING NEW ORDER -------')
                print('---------------------------------\n')

                time.sleep(1)
                candles, error_message = data_downloader.get_current_data('EUR_USD', ['bid', 'ask'], 'M30')

                if error_message is not None:
                    print(error_message)
                    break

                else:
                    last_candle = candles[-1]
                    curr_bid_open = float(last_candle.bid.o)
                    curr_ask_open = float(last_candle.ask.o)

                if pred == 'buy':
                    profit_price = round(curr_ask_open + (gain_risk_ratio * pips_to_risk), 5)

                else:
                    profit_price = round(curr_bid_open - (gain_risk_ratio * pips_to_risk), 5)

                print('Action: ' + str(pred))
                print('Profit price: ' + str(profit_price))
                print()

                order_handler.place_market_order(pred, n_units_per_trade, profit_price)

                # Give Oanda a few seconds to place the order
                time.sleep(15)

                open_trades, error_message = order_handler.get_open_trades()

                if error_message is None and len(open_trades) > 0:
                    order_in_place = True
                    print('Placed new order: ' + str(pred) + ' -- Num orders: ' + str(len(open_trades)))
                    continue

                else:
                    print('Error in placing trades')

                    if error_message is not None:
                        print(error_message)

                    return
        else:
            print('There is currently an open trade')

            open_trades, error_message = order_handler.get_open_trades()

            if error_message is not None:
                print('Error in getting open trades:\n' + error_message)
                continue

            if len(open_trades) == 0:
                order_in_place = False

        while datetime.now() < dt:
            time.sleep(1)


if __name__ == "__main__":
    main()
