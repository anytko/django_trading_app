"""
URL configuration for trading_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from accounts import urls as accounts_urls  # Import the URLs module from the accounts app
from transactions import urls as transactions_urls
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('portfolio/', include('portfolio.urls')),
    path('signup/', include(accounts_urls)),  # Include the URLs module for the accounts app
    path('', include('django.contrib.auth.urls')),
    path('transactions/', include(transactions_urls)),
    path('', RedirectView.as_view(url='/login/')),

]


