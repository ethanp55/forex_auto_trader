from sendgrid import SendGridAPIClient, Mail
from Oanda.Config.config import Config


class SendgridClient(object):

    @staticmethod
    def send_email(currency_pair, signal):
        message = Mail(from_email=Config.get_sendgrid_email(),
                       to_emails=Config.get_sendgrid_email(),
                       subject=currency_pair + ' ' + str(signal),
                       plain_text_content=str(signal) + ' signal on ' + str(currency_pair))

        try:
            sg = SendGridAPIClient(Config.get_sendgrid_api_token())
            response = sg.send(message)

            print(response.status_code)
            print(response.body)
            print(response.headers)

        except Exception as e:
            print('Error sending email:')
            print(e.message)
