import v20
from Oanda.Config.config import Config


"""
A class for placing trades
"""
class OrderHandler(object):

    @staticmethod
    def place_market_order(currency_pair, order_type, n_units, profit_price, stop_loss):
        # Add all of the needed arguments
        kwargs = {}
        kwargs['type'] = 'MARKET'
        kwargs['instrument'] = currency_pair
        kwargs['units'] = str(n_units) if order_type == 'buy' else str(-n_units)
        kwargs['timeInForce'] = 'FOK'
        kwargs['positionFill'] = 'DEFAULT'
        kwargs['takeProfitOnFill'] = {'price': str(profit_price), 'timeInForce': 'GTC'}
        # kwargs['stopLossOnFill'] = {'distance': str(pips_to_risk), 'timeInForce': 'GTC'}
        kwargs['stopLossOnFill'] = {'price': str(stop_loss), 'timeInForce': 'GTC'}
        # kwargs['trailingStopLossOnFill'] = {'distance': str(pips_to_risk), 'timeInForce': 'GTC'}

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

        print("Response: {} ({})\n{}".format(response.status, response.reason, response.body))

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
