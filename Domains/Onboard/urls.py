from django.urls import path
from .views import OnboardingAPIView

urlpatterns = [
    path('onboard/', OnboardingAPIView.as_view(), name='onboard'),
]