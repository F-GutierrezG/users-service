from flask import current_app
from .services import MailerServiceMock, MailerService


class MailerServiceFactory:
    def get_instance():
        if current_app.config['MAILER_SERVICE_MOCK']:
            return MailerServiceMock.get_instance()
        return MailerService()
