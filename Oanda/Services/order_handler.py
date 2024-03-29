import v20
from Oanda.Config.config import Config


"""
A class for placing trades
"""


class OrderHandler(object):

    @staticmethod
    def place_market_order(currency_pair, order_type, n_units, profit_price, stop_loss, pips_to_risk, use_trailing_stop):
        # Add all of the needed arguments
        kwargs = {}
        kwargs['type'] = 'MARKET'
        kwargs['instrument'] = currency_pair
        kwargs['units'] = str(
            n_units) if order_type == 'buy' else str(-n_units)
        kwargs['timeInForce'] = 'FOK'
        kwargs['positionFill'] = 'DEFAULT'
        kwargs['takeProfitOnFill'] = {
            'price': str(profit_price), 'timeInForce': 'GTC'}

        if use_trailing_stop:
            kwargs['trailingStopLossOnFill'] = {
                'distance': str(pips_to_risk), 'timeInForce': 'GTC'}

        else:
            kwargs['stopLossOnFill'] = {
                'price': str(stop_loss), 'timeInForce': 'GTC'}

        # Create the Oanda API context
        api_context = v20.Context(
            Config.get_host_name(),
            Config.get_port(),
            Config.get_ssl(),
            application="sample_code",
            token=Config.get_api_token(),
            datetime_format=Config.get_date_format()
        )

        # Use the Oanda API context as well as the key word arguments to place the order
        response = api_context.order.market(Config.get_account(), **kwargs)

        print("Response: {} ({})\n{}".format(
            response.status, response.reason, response.body))

    @staticmethod
    def get_open_trades():
        api_context = v20.Context(
            Config.get_host_name(),
            Config.get_port(),
            Config.get_ssl(),
            application="sample_code",
            token=Config.get_api_token(),
            datetime_format=Config.get_date_format()
        )

        response = api_context.trade.list_open(Config.get_account())

        if response.status != 200:
            return None, str(response) + '\n' + str(response.body)

        return response.body['trades'], None

    @staticmethod
    def update_trade_stop_loss(trade_id, new_stop_loss_price):
        kwargs = {}
        kwargs['stopLoss'] = {'price': str(new_stop_loss_price)}

        api_context = v20.Context(
            Config.get_host_name(),
            Config.get_port(),
            Config.get_ssl(),
            application="sample_code",
            token=Config.get_api_token(),
            datetime_format=Config.get_date_format()
        )

        response = api_context.trade.set_dependent_orders(
            Config.get_account(), trade_id, **kwargs)

        if response.status != 200:
            return str(response) + '\n' + str(response.body)

        return None

    @staticmethod
    def update_trade_take_profit(trade_id, new_take_profit_price):
        kwargs = {}
        kwargs['takeProfit'] = {'price': str(new_take_profit_price)}

        api_context = v20.Context(
            Config.get_host_name(),
            Config.get_port(),
            Config.get_ssl(),
            application="sample_code",
            token=Config.get_api_token(),
            datetime_format=Config.get_date_format()
        )

        response = api_context.trade.set_dependent_orders(
            Config.get_account(), trade_id, **kwargs)

        if response.status != 200:
            return str(response) + '\n' + str(response.body)

        return None

    @staticmethod
    def close_trade(trade_id, n_units):
        kwargs = {}
        kwargs['units'] = str(abs(n_units))

        api_context = v20.Context(
            Config.get_host_name(),
            Config.get_port(),
            Config.get_ssl(),
            application="sample_code",
            token=Config.get_api_token(),
            datetime_format=Config.get_date_format()
        )

        response = api_context.trade.close(
            Config.get_account(), trade_id, **kwargs)

        if response.status != 200:
            return str(response) + '\n' + str(response.body)

        return None
