from django.contrib.auth.forms import UserCreationForm
from .models import User
from . models import Payment, Loan, UserDocument, Withdrawal
from django import forms



class RegistrationForm(UserCreationForm):
    

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }





class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('mobile_number', 'usdt_trc20_wallet_address','eth_wallet_address', 'btc_wallet_address')

class DepositForm(forms.ModelForm):
    class Meta:
        model=Payment
        fields= ('user','payment_option', 'amount', 'memo')

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model=Withdrawal
        fields= ('amount', 'currency', 'wallet_address')

class LoanForm(forms.ModelForm):
    class Meta:
        model=Loan
        fields =  ('amount', 'duration', 'purpose')



class DocumentForm(forms.ModelForm):
    class Meta:
        model= UserDocument
        fields = ('governmental_document', 'proof_address', 'bank_statement')