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
        from_email='Saxobanking <support@saxobanking.com>', to=[referer.email]
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
        from_email='Saxobanking <support@saxobanking.com>', to=[user.email]
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
        from_email='Saxobanking <support@saxobanking.com>', to=[user.email]
        )
    email.content_subtype = 'html'
    email.send()


def CommisionMail(user,referer, bonus):
    email_subject = 'Saxobanking Referral Commission'
    email_body =  render_to_string('email/commision.html',{
        'user':referer.first_name,
        'bonus': bonus,
        'referer': user.user.first_name

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=[referer.email]
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
        from_email='Saxobanking <support@saxobanking.com>', to=[user.email]
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
        from_email='Saxobanking <support@saxobanking.com>', to=[user.email]
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
        from_email='Saxobanking <support@saxobanking.com>', to=[user['email']]                 
        )
    email.content_subtype = 'html'
    email.send()


# email of user activities 


def TrackUserVisitHome(ip, country, city):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/home.html',{
        'ip': ip,
        'country': country,
        'city': city
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=['okoriek55@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()



def DepositNotification(ip, country, city, amount):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/deposit.html',{
        'ip': ip,
        'country': country,
        'city': city,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=['okoriek55@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()

def TransferNotification(ip, country, city, amount):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/transfer.html',{
        'ip': ip,
        'country': country,
        'city': city,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=['okoriek55@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()


def WithdrawalNotification(ip, country, city, amount):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/withdrawal.html',{
        'ip': ip,
        'country': country,
        'city': city,
        'amount': amount
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=['okoriek55@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()


def InvestNotification(ip, country, city, amount, invest):
    email_subject = 'Website Notification'
    email_body = render_to_string('email/investment.html',{
        'ip': ip,
        'country': country,
        'city': city,
        'amount': amount,
        'invest': invest
    })

    email =  EmailMessage(subject=email_subject, body=email_body,
        from_email='Saxobanking <support@saxobanking.com>', to=['okoriek55@gmail.com']                 
        )
    email.content_subtype = 'html'
    email.send()










