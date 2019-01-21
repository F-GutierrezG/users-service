import json
import requests

from flask import current_app


class MailerService:
    def send(
            self, recipients, sender, subject, message, cc=None, bcc=None,
            reply_to=None):
        url = '{}/send'.format(current_app.config['MAILER_SERVICE_URL'])
        headers = {'Content-Type': 'application/json'}
        data = {
            'to': recipients,
            'from': sender,
            'subject': subject,
            'body': message,
            'cc': cc,
            'bcc': bcc,
            'reply_to': reply_to
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = json.loads(response.text)
        return response, data


class Response:
    status_code = 200


class MailerServiceMock:
    instance = None

    def __init__(self):
        self.clear()

    def clear(self):
        return MailerServiceMock.instance

    def send(
            self, recipients, sender, subject, message, cc=None, bcc=None,
            reply_to=None):
        return Response()
