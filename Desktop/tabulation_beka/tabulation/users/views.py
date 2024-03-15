from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate,login,logout



# Create your views here.
def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username_part_email = form.cleaned_data.get("email")
            username_part=username_part_email.split('@')
            username = username_part[0]
            user = authenticate(request, email=email, password=password,username=username)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    print('User is inactive.')
            else:
                print('Authentication failed.')
        else:
            print(form.errors)
    else:
        form = UserLoginForm(request)

    return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('users:login')

