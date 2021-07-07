from django.forms import ModelForm
from accounts.models import  Account

class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']
