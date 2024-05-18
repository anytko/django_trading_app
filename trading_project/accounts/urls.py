from django.urls import path
from .views import signup  # Import the signup view directly

urlpatterns = [
    # Other URL patterns
    path('', signup, name='signup'),
]
