from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import Portfolio

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

