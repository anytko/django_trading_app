from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Portfolio
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create and save a Portfolio instance for the new user
            portfolio = Portfolio.objects.create(user=user)
            portfolio.save()

            login(request, user)
            return redirect('portfolio')  # Redirect to the portfolio view after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('portfolio')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

