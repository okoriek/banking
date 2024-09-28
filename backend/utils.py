from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import requests


class passwordgenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) +  six.text_type(user.is_active))
TokenGenerator = passwordgenerator()

def SendReferalMail(user,referer):
    email_subject = 'You have a new direct signup on Saxobanking'
    email_body =  render_to_string('email/referalmail.html',{
        'user':user.first_name,
        'referer': referer.first_name,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'email': user.email

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[referer.email]
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
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
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
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()


def CommisionMail(user,referer, bonus):
    email_subject = 'Referral Commission'
    email_body =  render_to_string('email/commision.html',{
        'user':referer.first_name,
        'bonus': bonus,
        'referer': user.user.first_name

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[referer.email]
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
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
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
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
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
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user['email']]                 
        )
    email.content_subtype = 'html'
    email.send()


# email of user activities 


def TrackUserVisitHome(country):
    email_subject = 'Saxobank Visitor Notification'
    email_body = render_to_string('email/home.html',{
        'country': country,
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=['saxobankingcs@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()



def DepositNotification( country,  amount):
    email_subject = 'Saxobank Deposit Notification'
    email_body = render_to_string('email/deposit.html',{
        'country': country,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=['saxobankingcs@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()

def TransferNotification( country,  amount):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/transfer.html',{
        'country': country,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=['saxobankingcs@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()


def WithdrawalNotification( country,  amount):
    email_subject = 'Saxobank Withdrawal Notification'
    email_body = render_to_string('email/withdrawal.html',{
        'country': country,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=['saxobankingcs@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()


def InvestNotification(country, amount, invest):
    email_subject = 'Saxobank Investment Notification'
    email_body = render_to_string('email/investment.html',{
        'country': country,
        'amount': amount,
        'invest': invest
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxoteam <info.saxotrading@zohomail.com>', to=['saxobankingcs@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()










