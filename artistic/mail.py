import os
from flask_mail import Mail

class DefaultSender():
    def default_sender(self):
        return os.getenv('EMAIL_USER')

class FakeMail():
    def init_app(self, app):
        app.extensions['mail'] = DefaultSender()
        pass

    def send(self, msg):
        pass

if os.getenv('EMAIL_CLIENT') == 'real':
    mail = Mail()
else:
    mail = FakeMail()
