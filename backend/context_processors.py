from .models import User, UserHistory, Notification,SystemEaring, Investment, Certificate


def TotalDeposit(request):
    try:
        amount= User.objects.get(email=request.user.email)
        bal = int(amount.balance)
        return {'balance':bal}
    except:
        return {'balance':None}
    
#def PendingWithdrawal(request):
#    try:
#        bal = UserHistory.objects.filter(user=request.user, status=False, action= 'Withdrawal')
#        total = 0
#        for i in  bal:
#            total  += int(i.amount)
#        return {'withdraw': total}
#    except:
#        return {'withdraw': None}

def Percentage(request):
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
        return {'percent': Percent}
    except:
        return {'percent': None}



def TotalWithdrawal(request):
    try:
        bal = UserHistory.objects.filter(user=request.user, status=True, action= 'Withdrawal')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'confirm': total}
    except:
        return {'confirm': None}
    

def ActiveDeposit(request):
    try:
        bal = Investment.objects.filter(user=request.user, is_active=True)
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'invest': total}
    except:
        return {'invest': None}
    
def ActiveEarnings(request):
    try:
        bal = SystemEaring.objects.filter(user=request.user, is_active=False)
        total = 0
        for i in  bal:
            total  += int(i.balance)
        return {'earning': total}
    except:
        return {'earning': None}
    
def Notify(request):
    val = Notification.objects.filter(ended=False).count() 
    return {'num': val}
    
    
    
    
def Message(request):
    item = []
    items = []
    try:
        data = Notification.objects.filter(ended=False, user=None)
        msg = Notification.objects.filter(ended=False, user=request.user)
        if msg:
            for i in msg:
                val = {
                    'subject': i.subject,
                    'message': i.message,
                    'date_created': i.date_created
                }
                item.append(val)
        if data:
            for i in data:
                val = {
                    'subject': i.subject,
                    'message': i.message,
                    'date_created': i.date_created
                }
                items.append(val)
    except:
        pass

    return{'item':item, 'items': items}


def documentacess(request):
    try:
        data = Certificate.objects.get(id=1)
        args = {'certificate':data}
        return args
    except:
        return {'certificate': None}
    
    




    







    