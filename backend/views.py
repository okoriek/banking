from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .form import RegistrationForm
from django.contrib import messages
from .models import *
from .form import *
from django.contrib.auth.views import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .utils import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view




def home(request):
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    TrackUserVisitHome(ip, country, city)
 
    return render(request, 'backend/home.html')


def EmailVerification(request, uidb64, token):
    try:
        uid =  force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and TokenGenerator.check_token(user, token):
        user.is_active=  True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Email verification complete' )
        return redirect('/login')
    return JsonResponse('User verified', safe=False)


def register(request):
    if request.method=='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()
            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.first_name,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
                )
            email.content_subtype = 'html'
            email.send()
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:    
        form = RegistrationForm()
    args = {'form':form}
    return render(request, 'backend/register.html', args)


def ReferalRegister(request, referal):
    if request.method=='POST':
        referer =  User.objects.get(referal=referal)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()


            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.first_name,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='Echelonglobe <support@echelonglobe.com>', to=[user.email]
                ) 
            email.content_subtype = 'html'
            email.send()
            SendReferalMail(user,referer)
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:     
        form = RegistrationForm()
    args = {'form':form}
    return render(request, 'backend/register.html', args)




@login_required(login_url='/login/')  
def Dashboard(request):
    user = request.user
    data = History.objects.filter(user = user)[:10]
    detail = User.objects.get(email= request.user.email)

    #referer

    refer = User.objects.all().filter(refered_by = str(request.user))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'detail':detail, 'data':data, 'total':refer.count(), 'refer': detail.referal, 'earnings':total}
    return render(request, 'dashboard/dashboard.html', arg)




@login_required(login_url='/login/')
def Deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            ip = request.user_location.get('ip')
            city = request.user_location.get('city')
            country = request.user_location.get('country')
            current = form.save(commit=False)
            current.user= request.user
            current.save()
            DepositNotification(ip=ip, country=country, city=city, amount=current.amount)
            bills = Payment.objects.last()
            qrcode =  Currency.objects.filter(name=bills.payment_option).last()
            return render(request, 'dashboard/confirmpayment.html', {'currency':current.payment_option, 'amount':current.amount, 'type':qrcode})
    else:
        form = DepositForm()
    arg = {'form':form}
    return render(request, 'dashboard/deposit.html', arg)

@login_required(login_url='/login/')
def ConfirmPayment(request):
    user = request.user
    bill = Payment.objects.filter(user = user).last()
    return JsonResponse('Admin Notified About Payment', safe=False)
    
@login_required(login_url='/login/')  
def profiledetails(request):
    detail =  User.objects.get(email = request.user.email)
    arg = {'details':detail}
    return render(request, 'dashboard/profiledetails.html', arg)

@login_required(login_url='/login/')  
def Referal(request):
    detail =  User.objects.get(email = request.user.email)
    refer = User.objects.all().filter(refered_by = str(request.user.pk))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user.email))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'total':refer.count(), 'refer': detail.referal, 'earning':total}
    return render(request, 'dashboard/referal.html', arg)

@login_required(login_url='/login/')  
def history(request):
    user = request.user
    data = History.objects.filter(user = user)
    args = {'data':data}
    return render(request, 'dashboard/history.html', args)

@login_required(login_url='/login/')
def editProfile(request):
    if request.method=='POST':
        forms = UserForm(request.POST, instance = request.user)
        if forms.is_valid():
            data = forms.save()
            messages.add_message(request, messages.SUCCESS, 'Profile updated!',)
            return redirect('/edit_personal_details')
            
    else:
        forms =  UserForm(instance=request.user)
    args = {'forms':forms}
    return render(request, 'dashboard/editprofile.html' , args)


@login_required(login_url='/login/') 
def RenderWithdrawal(request):
    data =  Currency.objects.all()
    amount = MinimumWithdraw.objects.filter().last()
    args = {'data':data, 'min':amount}
    return render(request, 'dashboard/withdrawal.html', args)

@login_required(login_url='/login/') 
def MakeWithdrawal(request):
    amount = request.POST['amount']
    select = request.POST['select']
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    withdraw = Withdrawal.objects.create(user= request.user, currency = select, amount= amount)
    withdraw.save()
    bal =  User.objects.get(email= request.user.email)
    bal.balance -= int(amount)
    bal.save()
    WithdrawalNotification(ip=ip, country=country, city=city, amount=amount)
    return JsonResponse('Succesfully placed withdrawal', safe=False)


def Contactinfo(request):
        
    
    return render(request, 'backend/contact.html')


def terms(request):

    return render(request, 'backend/terms.html')


def AdminContact(request):
    name = request.POST['name']
    email = request.POST['email']
    message = request.POST['message']
    data = Contact.objects.create(name=name, email=email, message=message)
    data.save()
    return JsonResponse('DATA SUBMITTED', safe=False)



def About(request):
    return render(request, 'backend/about.html')



def investment(request):
    
    return render(request, 'backend/investment.html')



# Initiating all type of Investment

# housing

@login_required(login_url='/login/') 
def EstateActiveInvestment(request):
    invest =  RealEstate.objects.all().values
    args = {'invest':invest}
    return render(request, 'dashboard/realestate.html', args)

@login_required(login_url='/login/') 
def EstateSubmitInvestment(request):
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    id = request.POST['pk']
    house = RealEstate.objects.get(pk=id)
    invest =  Investment.objects.create(user = request.user, real_estate=house, amount=house.amount, is_active=True)
    InvestNotification(ip=ip, country=country, city=city, amount=house.amount, invest='Real Estate')
    return JsonResponse('Investment successful', safe=False)


# mutual funds

@login_required(login_url='/login/') 
def MutualActiveInvestment(request):
    invest =  MutualFund.objects.all().values
    args = {'invest':invest}
    return render(request, 'dashboard/mutual.html', args)

@login_required(login_url='/login/') 
def MutualSubmitInvestment(request):
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    id = request.POST['pk']
    house = MutualFund.objects.get(pk=id)
    invest =  Investment.objects.create(user = request.user, mutual_fund=house, amount=house.amount, is_active=True)
    InvestNotification(ip=ip, country=country, city=city, amount=house.amount, invest='Mutual Funds(MFs)')
    return JsonResponse('Investment successful', safe=False)



# certificate of deposit

@login_required(login_url='/login/') 
def CertificateActiveInvestment(request):
    invest =  CertificateOfDeposit.objects.all().values
    args = {'invest':invest}
    return render(request, 'dashboard/saving.html', args)

@login_required(login_url='/login/') 
def CertificateSubmitInvestment(request):
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    id = request.POST['pk']
    house = CertificateOfDeposit.objects.get(pk=id)
    invest =  Investment.objects.create(user = request.user, certificate_of_deposit=house, amount=house.amount, is_active=True)
    InvestNotification(ip=ip, country=country, city=city, amount=house.amount, invest='Certificate of Deposit')
    return JsonResponse('Investment successful', safe=False)



# dividend per share

@login_required(login_url='/login/') 
def DividendInvestment(request):
    invest =  DividendPerShare.objects.all().values
    args = {'invest':invest}
    return render(request, 'dashboard/dividend.html', args)

@login_required(login_url='/login/') 
def DividendSubmitInvestment(request):
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    id = request.POST['pk']
    house = DividendPerShare.objects.get(pk=id)
    invests =  Investment.objects.create(user = request.user, dividend_per_share=house, amount=house.amount, is_active=True)
    InvestNotification(ip=ip, country=country, city=city, amount=house.amount, invest='Dividend Per Share')
    return JsonResponse('Investment successful', safe=False)






def Faq(request):

    return render(request, 'backend/faq.html')

@login_required(login_url='/login/') 
def transfer(request):
    amount = request.POST['amount']
    username = request.POST['username']
    ip = request.user_location.get('ip')
    city = request.user_location.get('city')
    country = request.user_location.get('country')
    transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = False  )
    transfer.save()
    TransferNotification(ip=ip, country=country, city=city, amount=amount)

    return JsonResponse('Transfer Pending', safe=False)


@login_required(login_url='/login/') 
def InitiateTransfer(request):
    
    return render(request, 'dashboard/transfer.html')



@login_required(login_url='/login/') 
def notification(request):
    
    return render(request, 'backend/tr.html')


# Api endpoint for validating earning and investment
@api_view(['GET','POST', 'PUT'])
def validateEarning(request):
    earn =  SystemEaring.objects.filter(is_active=True)
    invest =  Investment.objects.filter(is_active=True)
    for x in earn: 
        x.save()
    for y in invest:
        y.save()
    return Response({'message': 'Processed Successfully'}, status=status.HTTP_202_ACCEPTED)


#Email view organisation

def DisplayEmail(request):

    return render(request, 'dashboard/mailsending.html')


def SendBulkEmail(request):
    email  =  request.POST['email']
    subject =  request.POST['subject']
    val = request.POST['value']
    message =  request.POST['message']

    if val == 'true':
        item = User.objects.all()
        for i in item:
            user = {
                'username': i.first_name,
                'email': i.email
            }
            SendEmail(subject, user, message)
    else:
        item = User.objects.filter(email = email)
        for i in item:
            user = {
                'username': i.first_name,
                'email': i.email
            }
            SendEmail(subject, user, message)
    return JsonResponse({'message': 'Email Successfully Sent'})



# Loan rendering

def loan(request):

    return render(request, 'backend/loan.html')






