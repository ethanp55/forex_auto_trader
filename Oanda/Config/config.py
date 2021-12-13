from os import environ, stat

config_vars = {
    'host_name': environ['HOST_NAME'],
    'streaming_host_name': environ['STREAMING_HOST_NAME'],
    'port': environ['OANDA_PORT'],
    'ssl': environ['SSL'],
    'api_token': environ['API_TOKEN'],
    'date_format': environ['DATE_FORMAT'],
    'time_zone': environ['TIME_ZONE'],
    'account': environ['ACCOUNT'],
    'sendgrid_api_token': environ['SENDGRID_API_TOKEN'],
    'sendgrid_email': environ['SENDGRID_EMAIL']
}


class Config(object):

    @staticmethod
    def get_host_name():
        return config_vars['host_name']

    @staticmethod
    def get_streaming_host_name():
        return config_vars['streaming_host_name']

    @staticmethod
    def get_port():
        return config_vars['port']

    @staticmethod
    def get_ssl():
        return config_vars['ssl']

    @staticmethod
    def get_api_token():
        return config_vars['api_token']

    @staticmethod
    def get_date_format():
        return config_vars['date_format']

    @staticmethod
    def get_time_zone():
        return config_vars['time_zone']

    @staticmethod
    def get_account():
        return config_vars['account']

    @staticmethod
    def get_sendgrid_api_token():
        return config_vars['sendgrid_api_token']

    @staticmethod
    def get_sendgrid_email():
        return config_vars['sendgrid_email']
