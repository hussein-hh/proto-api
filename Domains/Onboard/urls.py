from django.urls import path
from .views import onboarding

urlpatterns = [
    path('onboard/', onboarding, name='onboard'),
]