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
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone




def home(request):
    
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
    


def register(request):
    if request.method=='POST':
        code = request.POST.get('country_phone_code')
        mobile = request.POST.get('phone_number')
        country = request.POST.get('country')

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.country = country
            user.mobile_number = f"{code}{mobile}"
            user.balance = 50
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
                from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
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
        code = request.POST.get('country_phone_code')
        mobile = request.POST.get('phone_number')
        country = request.POST.get('country')
        referer =  User.objects.get(referal=referal)

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.country = country
            user.mobile_number = f"{code}{mobile}"
            user.balance = 100
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
                from_email='Saxoteam <info.saxotrading@zohomail.com>', to=[user.email]
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
    data = UserHistory.objects.filter(user = user)[:8]
    detail = User.objects.get(email= request.user.email)

    refer = User.objects.all().filter(refered_by = str(request.user))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'detail':detail, 'data':data, 'total':refer.count(), 'refer': refer.count(), 'earnings':total}
    return render(request, 'dashboard/dashboard.html', arg)




@login_required(login_url='/login/')
def Deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            country = request.user.country.name
            current = form.save(commit=False)
            current.user= request.user
            current.save()
            DepositNotification(country=country, amount=current.amount)
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
    data = UserHistory.objects.filter(user = user)
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
    user = User.objects.get(email = request.user.email)
    min = MinimumWithdraw.objects.filter().last()
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            if form_data.amount > user.balance:
                messages.success(request, 'Insufficient Amount balance')
                return redirect('/withdrawal')
            elif form_data.amount < min.amount:
                messages.success(request, f"minimum withdrawal is {min.amount}")
                return redirect('/withdrawal')
            else:
                form_data.user = request.user
                form_data.save()
                country = user.country.name
                amount = form_data.amount
                WithdrawalNotification(country, amount)
                messages.success(request, 'Request for Withdrawal Successful.')
                return redirect('/withdrawal')
    else:
        form = WithdrawalForm()
    args = {'form': form, 'min': min, 'bal':user}
    return render(request, 'dashboard/withdrawal.html', args)



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
    return render(request, 'investment/realestate.html', args)

@login_required(login_url='/login/') 
def EstateSubmitInvestment(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = RealEstate.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, real_estate=house, choice=house.name, amount=amount, returns=interest,  is_active=True)
        invest = 'Real Estate Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)


# mutual funds

@login_required(login_url='/login/') 
def AnnutiesActiveInvestment(request):
    invest =  Annuties.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/annuties.html', args)

@login_required(login_url='/login/') 
def AnnutiesSubmitInvestment(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Annuties.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, annuties=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Annuties Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)



# certificate of deposit

@login_required(login_url='/login/') 
def ArbitrageActiveInvestment(request):
    invest =  Arbitrage.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/arbitrage.html', args)

@login_required(login_url='/login/') 
def ArbitrageSubmitInvestment(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Arbitrage.objects.get(pk=id)
    user = User.objects.get(email = request.user.email)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, arbitrage=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Arbitrage Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)



# dividend per share

@login_required(login_url='/login/') 
def HalalActiveInvestment(request):
    invest =  HalalInvestment.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/halainvest.html', args)

@login_required(login_url='/login/') 
def HalalSubmitInvestment(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = HalalInvestment.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, hala_investment=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Halal Investment'
        InvestNotification(country, amount, invest)
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)




@login_required(login_url='/login/') 
def CryptoInvestment(request):
    invest =  Cryptocurrency.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/crypto.html', args)

@login_required(login_url='/login/') 
def CryptoSubmitInvestment(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Cryptocurrency.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, cryptocurrency=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Cryptocurrency Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)


#  Trading investments

@login_required(login_url='/login/') 
def StockTrading(request):
    invest =  Stocks.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/stock.html', args)

@login_required(login_url='/login/') 
def StockSubmitTrading(request):
    country = request.user_location.get('country')
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Stocks.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, stocks=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Stocks Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)

@login_required(login_url='/login/') 
def ForexTrading(request):
    invest =  Forex.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/forex.html', args)

@login_required(login_url='/login/') 
def ForexSubmitTrading(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Forex.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, forex=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        
        invest = 'Forex Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)

@login_required(login_url='/login/') 
def ShareTrading(request):
    invest =  Shares.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/share.html', args)

@login_required(login_url='/login/') 
def ShareSubmitTrading(request):
    country = request.user.country.name
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Shares.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, shares=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        
        invest = 'Shares Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)

@login_required(login_url='/login/') 
def NfpTrading(request):
    invest =  Nfp.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/nfp.html', args)

@login_required(login_url='/login/') 
def NfpSubmitTrading(request):
    country = request.user_location.get('country')
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    interest = (((amount * house.interest)/100) * house.duration) + amount
    house = Nfp.objects.get(pk=id)
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, nfp=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Nfp Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)

@login_required(login_url='/login/') 
def EnergyTrading(request):
    invest =  Energy.objects.all().values
    args = {'invest':invest}
    return render(request, 'investment/energy.html', args)

@login_required(login_url='/login/') 
def EnergySubmitTrading(request):
    country = request.user_location.get('country')
    id = request.POST['pk']
    amount = int(request.POST['amount'])
    house = Energy.objects.get(pk=id)
    interest = (((amount * house.interest)/100) * house.duration) + amount
    user = User.objects.get(email = request.user.email)
    if amount >= house.min and amount <= house.max and user.balance >= amount:
        user = User.objects.get(email = request.user.email)
        user.balance -= amount
        user.save()
        invests =  Investment.objects.create(user = request.user, energy=house, choice=house.name, returns=interest, amount=amount, is_active=True)
        invest = 'Energy Investment'
        try:
            InvestNotification(country, amount, invest)
        except:
            pass
        return JsonResponse('Your Investment has been Initiated successfully', safe=False)
    else:
        pass
        return JsonResponse('Invalid Amount', safe=False)






def Faq(request):

    return render(request, 'backend/faq.html')

@login_required(login_url='/login/') 
def transfer(request):
    amount = request.POST['amount']
    username = request.POST['username']
    bank = request.POST['bank']
    country = request.user.country.name
    if bank is not None:
        transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = False, bank_name=bank, is_external_transfer=True)
    else:
        transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = False  )

    TransferNotification(country=country, amount=amount)

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



# user document
@login_required(login_url='/login/')

def document(request):
    try:
        verify = UserDocument.objects.get(user=request.user)
        if verify.approve == True:
            return redirect('/Profile-dashboard')
        elif verify.submitted:
            return render(request, 'dashboard/document.html')            
    except:
        if request.method == 'POST':
            form =  DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = request.user
                data.submitted = True
                data.save()
                messages.success(request, 'Document Submitted, Awaiting Verification...')
                return redirect('/upload_document')
        else:
            form = DocumentForm()
        arg = {'form': form}
        return render(request, 'dashboard/document.html', arg)
        
    






# Loan rendering

@login_required(login_url='/login/')
def loan(request):
    loan_eligibily = UserDocument.objects.filter(user = request.user)
    if loan_eligibily.exists():
        if request.method == 'POST':
            form = LoanForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = request.user
                data.save()
                messages.success(request, 'Application submitted, awaiting Approval')
                return redirect('/loan_request')
            else:
                messages.error(request, 'Error processing form contact support')
        else:
            form = LoanForm()
        arg = {'form':form}
        return render(request, 'dashboard/loan.html', arg)
    else:
        return redirect('/upload_document')
    



# analytic 
@csrf_exempt
def analyticdata(request):
    try:
        invest = Investment.objects.filter(user=request.user, is_active=False)
        earning =  SystemEaring.objects.filter(user=request.user, is_active=False)
        invest_total = 0
        earning_total = 0 
        for i in invest:
            invest_total += i.amount
        for e in earning:
            earning_total += e.balance
        Percent =  (earning_total * 100)/invest_total
        return JsonResponse({'percent': Percent})
    except:
        return JsonResponse({'percent': 0})
    


def investmenthistory(request):
    
    invest = Investment.objects.filter(user= request.user)
    arg = {'data': invest}
    return render(request, 'dashboard/investhistory.html', arg)


    
    






