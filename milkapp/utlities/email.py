from django.core.mail import EmailMessage
from django.conf import settings


def send_email(instance):
    email = EmailMessage(
        'Regarding Your Complain : {}'.format(instance.title),
        instance.answer,
        settings.MAIN_EMAIL,
        [instance.customer.user.email]
    )
    email.content_subtype = "html" # this is the crucial part
    email.send()

def send_rejection(instance):
    email = EmailMessage(
        'Regarding Your Request for Credits'.format(instance.amount),
        'Sorry, we could not verify the authenticity of your application, hence it has been rejected.\n\
            If You Think this is a mistake,please file a complaint using the app\n',
        settings.MAIN_EMAIL,
        [instance.customer_id.user.email]
    )
    email.send()


def reset_mail(code,user):
    email = EmailMessage(
        'Password Reset Requested For Doodhwaley',
        'Your Reset Code is : {}'.format(code),
        settings.MAIN_EMAIL,
        [user.email]
    )
    email.content_subtype = "html" # this is the crucial part
    email.send()