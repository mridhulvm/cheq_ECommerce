from django.shortcuts import redirect

# Create your views here.
#===========================referral session creation

def referralSignup(request,referral_code):
    if request.session.get('ref_code'):
        del request.session['ref_code']
    request.session['ref_code']=referral_code
    return redirect('signup')