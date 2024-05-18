from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('reset-account/', views.reset_account, name='reset_account'),
]

