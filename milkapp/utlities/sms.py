from twilio.rest import Client

from django.conf import settings


client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
#
def send_msg(to="+923060698544", from_="+17479980870", body="8392"):
    message = client.messages.create(
        to=to, 
        from_=from_,
        body=body)
