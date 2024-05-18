from django.urls import path
from . import views

app_name = 'transactions'  # Namespace for the transactions app

urlpatterns = [
    path('', views.transaction_history, name='transaction_history'),
    # Other URL patterns for the transactions app
]