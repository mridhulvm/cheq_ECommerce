from django.shortcuts import render

# from .forms import AccountForm
# from .models import Account

# # Create your views here.
# def signup(request):
#     form = AccountForm(request.POST)
#     if request.method == 'POST':

        
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             phone_number = form.cleaned_data['phone_number']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             username = form.cleaned_data['username']
#             print(phone_number)
#             user = Account.objects.create(first_name = first_name, last_name = last_name, phone_number = phone_number,email = email,password = password,username = username)

#             user.save()
#     else:
#         form = AccountForm()

#     context = {
#         'form': form
#     }
#     return render(request,'accounts/signup.html',context)

# def signin(request):
#     return render(request,'accounts/signin.html')

# def signout(request):
#     return render(request,'accounts/signup.html')
