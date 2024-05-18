from django.urls import path
from .views import signup, login_view, logout_view  # Import the signup view directly

urlpatterns = [
    # Other URL patterns
    path('', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

