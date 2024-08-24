from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


class passwordgenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) +  six.text_type(user.is_active))
TokenGenerator = passwordgenerator()

def SendReferalMail(user,referer):
    email_subject = 'You have a new direct signup on Echelonglobe'
    email_body =  render_to_string('email/referalmail.html',{
        'user':user.first_name,
        'referer': referer.first_name,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'email': user.email

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[referer.email]
        )
    email.content_subtype = 'html'
    email.send()


def DepositMail(user,amount,currency):
    email_subject = 'Deposit has been approved'
    email_body =  render_to_string('email/depositmail.html',{
        'user':user.first_name,
        'amount': amount,
        'currency': currency
    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()


def WithdrawalMail(user, amount):
    email_subject = 'your withdrawal request has been approved'
    email_body =  render_to_string('email/withdrawalmail.html',{
        'user':user.first_name,
        'amount': amount,
    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()


def CommisionMail(user,referer, bonus):
    email_subject = 'Echelonglobe Referral Commission'
    email_body =  render_to_string('email/commision.html',{
        'user':referer.first_name,
        'bonus': bonus,
        'referer': user.user.first_name

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[referer.email]
        )
    email.content_subtype = 'html'
    email.send()


def TransferMail(user,referer, amount):
    email_subject = 'Internal Fund Transfer'
    email_body =  render_to_string('email/transferemail.html',{
        'user': user,
        'amount': amount,
        'referer': referer

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()

def TransferRecieverMail(referer, amount, user):
    email_subject = 'Internal Fund Transfer'
    email_body =  render_to_string('email/transferemail.html',{
        'user': user,
        'amount': amount,
        'referer': referer

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()


def SendEmail(subject, user, message):
    email_subject = subject
    email_body = render_to_string('email/sendbulkmail.html',{
        'user': user,
        'subject': subject,
        'message': message
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Echelonglobe <support@echelonglobe.com>', to=[user['email']]                 
        )
    email.content_subtype = 'html'
    email.send()




