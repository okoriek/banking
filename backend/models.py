from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission, PermissionsMixin
from django.utils import timezone
import random
from decimal import Decimal
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField
import qrcode
from django.core.files import File
from PIL import Image, ImageDraw
from io import BytesIO
from .utils import WithdrawalMail, CommisionMail, DepositMail, TransferMail, TransferRecieverMail
from phonenumber_field.modelfields import PhoneNumberField

class MyUserManager(BaseUserManager):
    def create_user(self,email, first_name, last_name, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not first_name:
            raise ValueError('User must enter first name')
        
        if not last_name:
            raise ValueError('User must enter last name')

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email,password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name=last_name,
            password=password,
        )

        permission = Permission.objects.all()

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.user_permissions.set(permission)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name    = models.CharField(max_length=100, blank=True, null=True)
    last_name    = models.CharField(max_length=100, blank=True, null=True)
    email         = models.EmailField(max_length=100, unique=True)
    referal = models.CharField(max_length=20, unique=True, blank=True, null=True)
    refered_by = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(default=0, blank=True, null=True,decimal_places=2, max_digits=20)
    country = CountryField(blank_label="(select country)")
    btc_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    eth_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    usdt_trc20_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    mobile_number = models.CharField(max_length=25, blank=True, null=True)
    document_verified =  models.BooleanField(default=False)

    
    
    date_joined   = models.DateTimeField(auto_now_add=True) 
    last_login    = models.DateTimeField(auto_now_add=True)   
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    objects = MyUserManager()


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        self.referal = f"{self.pk}{self.first_name}{self.pk}"
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_superadmin

    def has_module_perms(self, add_label):
        return self.is_superadmin
    


class Contact(models.Model):
    name =  models.CharField(max_length=300)
    email =  models.EmailField(max_length=200)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.name}---------{self.email}"
    

class Currency(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    rate = models.CharField(max_length=20, blank=True, null=True)
    wallet_id = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='wallet/', blank=True, null=True)

    class Meta:
        verbose_name_plural='Currencies'

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        img = qrcode.make(self.wallet_id)
        canvas = Image.new('RGB',(390,390), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(img)
        name = f'{self.name}QRCODE.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.image.save(name, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)




class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    payment_option= models.ForeignKey(Currency, on_delete=models.DO_NOTHING, blank=True, null=True)
    amount = models.DecimalField(blank=True, decimal_places=2, max_digits=20)
    memo = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.payment_option}-------------{self.amount}"
    
    def save(self, *args, **kwargs):
        if self.status == True:
            account = self.user
            payment = Currency.objects.get(name = str(self.payment_option))
            total = self.amount
            account.balance += total
            account.save()
            amount = self.amount
            user = self.user
            currency = self.payment_option
            reinvestment =  Reinvestment.objects.filter(user = user)
            for i in reinvestment:
                i.number_of_investment = 0
                i.save()
            DepositMail(user,amount, currency)
        super().save(*args, **kwargs)


# Multiple Investment

class RealEstate(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"


   


class HalalInvestment(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"


   


class Arbitrage(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"



class Annuties(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name_plural = 'Annuties'
    

    def __str__(self):
        return f"{self.name}"



class Stocks(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = 'Stocks'


   



class Forex(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = 'Forex'


    


class Shares(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name_plural = 'Shares'


   



class Nfp(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.name}"


 


class Energy(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name_plural = 'Energies'

    def __str__(self):
        return f"{self.name}"


   

class Cryptocurrency(models.Model):
    name =  models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    min = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    max = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    interest = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)
    duration =  models.IntegerField(blank=True, null=True, default=0)
    slot =  models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name_plural = 'Cryptocurrencies'

    def __str__(self):
        return f"{self.name}"


   








class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE, blank=True, null=True)
    halal_investment = models.ForeignKey(HalalInvestment, on_delete=models.CASCADE, blank=True, null=True)
    annuties = models.ForeignKey(Annuties, on_delete=models.CASCADE, blank=True, null=True)
    arbitrage = models.ForeignKey(Arbitrage, on_delete=models.CASCADE, blank=True, null=True)
    stocks = models.ForeignKey(Stocks, on_delete=models.CASCADE, blank=True, null=True)
    forex = models.ForeignKey(Forex, on_delete=models.CASCADE, blank=True, null=True)
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, blank=True, null=True)
    shares = models.ForeignKey(Shares, on_delete=models.CASCADE, blank=True, null=True)
    nfp = models.ForeignKey(Nfp, on_delete=models.CASCADE, blank=True, null=True)
    energy = models.ForeignKey(Energy, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(default=timezone.now) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}--------{self.amount}------------{self.date_created}"
    
    def save(self, *args, **kwargs):

        def duration():
            if self.real_estate:
                return self.real_estate.duration
            elif self.halal_investment:
                return self.halal_investment.duration
            elif self.annuties:
                return self.annuties.duration
            elif self.arbitrage:
                return self.arbitrage.duration
            elif self.stocks:
                return self.stocks.duration
            elif self.shares:
                return self.shares.duration
            elif self.forex:
                return self.forex.duration
            elif self.nfp:
                return self.nfp.duration
            elif self.cryptocurrency:
                return self.cryptocurrency.duration
            else:
                return self.energy.duration
        
        self.date_expiration =  self.date_created + timezone.timedelta(days=duration())
        if timezone.now() > self.date_expiration and self.is_active == True and self.is_completed == False:
            total =  User.objects.get(user=self.user)
            total.balance += self.amount
            total.save()
            self.is_active = False
            self.is_completed =True
        super().save(*args, **kwargs)



class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    status = models.BooleanField(default=False)
    btc_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    eth_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    usdt_trc20_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.currency}---------{self.amount}"
    
    def save(self, *args, **kwargs):
        self.btc_wallet_address = self.user.btc_wallet_address
        self.eth_wallet_address = self.user.eth_wallet_address
        self.usdt_trc20_wallet_address = self.user.usdt_trc20_wallet_address
        user = self.user
        amount = self.amount
        if self.status == True:
            WithdrawalMail( user, amount)
        else:
            pass
        super().save(*args, **kwargs)
    

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    reciever = models.CharField(max_length=20, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    is_external_transfer = models.BooleanField(default=False)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.amount}------------{self.reciever}"
    
    def save(self, *args, **kwargs):
        user =  self.user
        amount =  self.amount
        referer =  self.reciever
        if self.status == False:
            TransferMail(user,referer,amount)
            TransferRecieverMail(referer, amount, user)
            bal =  User.objects.get(email= self.user.email)
            bal.balance -= int(amount)
            try:
                recieved = User.objects.get(email=self.reciever)
                custom = User.objects.get(email= recieved.email)
                custom.balance += int(amount)
                custom.save()
            except:
                pass
            bal.save()
        else:
            pass
        super().save(*args, **kwargs)
    

class Notification(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    subject =  models.CharField(max_length=100, blank=True, null=True)
    message  =  models.TextField( blank=True, null=True)
    ended =  models.BooleanField(default=False)
    date_created =  models.DateTimeField(default=timezone.now)
    date_expiring =  models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.subject
    
    def save(self, *args, **kwargs):
        if self.date_expiring == timezone.now:
            self.ended = True
        super().save(*args, **kwargs)
    


class SystemEaring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    invest = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    num =  models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)   
    balance = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    date_expiration =  models.DateTimeField(default=timezone.now)
    date_created =  models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        
        # Function that returns investment interests

        def investment():
            if self.invest.real_estate:
                return self.invest.real_estate.interest
            elif self.invest.annuties:
                return self.invest.annuties.interest
            elif self.invest.arbitrage:
                return self.invest.arbitrage.interest
            elif self.invest.cryptocurrency:
                return self.invest.cryptocurrency.interest
            elif self.invest.halal_investment:
                return self.invest.halal_investment.interest
            elif self.invest.nfp:
                return self.invest.nfp.interest
            elif self.invest.stocks:
                return self.invest.stocks.interest
            elif self.invest.shares:
                return self.invest.shares.interest
            elif self.invest.forex:
                return self.invest.forex.interest
            else:
                return self.invest.energy.interest
            

        total =  User.objects.filter(email=self.user)
        fig =  timezone.now().date() - self.date_created.date()
        diff = fig.days
        profit =  investment()
        profit_per_day = ((profit * int(self.invest.amount)))/100

        if diff == 0:
            pass
        else:
            if timezone.now() <= self.date_expiration: 
                if ((diff + 1) - self.num) == 1:
                    self.num += 1
                else:
                    self.num = diff + 1                          
            else:
                total =  User.objects.get(user=self.user)
                total.balance += profit_per_day
                total.save()
                self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}---------{self.balance}============{self.is_active}"
    
    



class ReferalBonus(models.Model):
    user =  models.CharField(max_length=200, blank=True, null=True)
    earnings = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)

    class Meta:
        verbose_name_plural='Referal Bonuses'



    def __str__(self):
        return f" {self.user}--------{self.earnings}"
    
    def save(self, *args, **kwargs):
        try:
            refer = User.objects.get(username = self.user)
            referer= refer
            bal =  User.objects.get(user = refer.pk)
            bal.balance += self.earnings
            user = User.objects.filter(refered_by = self.user).last()
            bal.save()
            bonus = self.earnings
            CommisionMail(user,referer, bonus)
        except:
            pass  
        super().save(*args, **kwargs )

class Reinvestment(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, blank=True, null=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return f"{self.user}-------{self.number_of_investment}"


class MinimumWithdraw(models.Model):
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=20)

    def __str__(self):
        return f"Mininum withdrawal: {self.amount}"
    

class UserDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    governmental_document = models.FileField(upload_to='government/')
    proof_address =  models.FileField(upload_to='address/')
    bank_statement =  models.FileField(upload_to='bank_document/')
    approve  = models.BooleanField(default=False) 
    


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} email: {self.user.email}  Approved: {self.approve}"  

    def save(self, *arg, **kwargs):
        if self.approve == True:
            self.user.is_verified = True

        super().save(*arg, **kwargs)

    



class Loan(models.Model):
    choice = (
        ('three_months', '3 months'),
        ('six_months', '6 months'),
        ('one_year', '1 year'),
    )
    user  = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    purpose =  models.TextField(max_length=5000, blank=True, null=True)
    amount = models.IntegerField(default='', blank=True, null=True)
    interest = models.IntegerField(default='', blank=True, null=True)

    status = models.BooleanField(default=False)
    duration = models.CharField(max_length=20, choices=choice)
    date_generated = models.DateTimeField(default=timezone.now)
    expiration = models.DateTimeField(default=timezone.now)




    def save(self, *arg, **kwargs):
        if self.duration == 'three_months':
            self.interest = (5*self.amount)/100
            self.expiration = self.date_generated + timezone.timedelta(days=91)
        elif self.duration == 'six_months':
            self.interest = (10*self.amount)/100
            self.expiration = self.date_generated + timezone.timedelta(days=183)
        else:
            self.interest = (15*self.amount)/100
            self.expiration = self.date_generated + timezone.timedelta(days=365)

        if self.status == True:
            user = User.objects.get(email=self.user.email)
            user.balance += self.amount
            user.save()
        else:
            pass
        super().save(*arg, **kwargs)

    def __str__(self):
        return f"user:{self.user} amount:{self.amount}"
    



class UserHistory(models.Model):
    choice  =  (
        ('Withdrawal', 'Withdrawal'),
        ('Deposit', 'Deposit'),
        ('Transfer', 'Transfer'),
        ('Investment', 'Investment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    withdraw = models.ForeignKey(Withdrawal, on_delete=models.CASCADE, blank=True, null=True)
    invest = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True, null=True)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, blank=True, null=True)
    action =  models.CharField(max_length=200, choices=choice, blank=True, null=True, editable=False)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.CharField(max_length=20)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)
    expires = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural ='Histories'
        ordering = ('-date_created',)

    def __str__(self):
        return f"{self.user}----------{self.amount}-------{self.action}------------{self.date_created}-------{self.status}"
    

class Ipaddress(models.Model):
    ip =  models.GenericIPAddressField(blank=True, null=True, max_length=50)

    def __str__(self):
        return self.ip
    
    class Meta:
        verbose_name_plural = 'Ipaddress'



class Certificate(models.Model):
    report1 = models.FileField(upload_to='certificate/', blank=True)
    report2 = models.FileField(upload_to='certificate/', blank=True)
    report3 = models.FileField(upload_to='certificate/', blank=True)
    white_paper = models.FileField(upload_to='certificate/', blank=True)
    complaint_handling = models.FileField(upload_to='certificate/', blank=True)
    conflict_interest = models.FileField(upload_to='certificate/', blank=True)
    private_policy = models.FileField(upload_to='certificate/', blank=True)

    


    def __str__(self):
        return f'Company certificate'
    






