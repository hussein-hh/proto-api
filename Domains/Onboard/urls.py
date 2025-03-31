from django.urls import path
from .views import UserOnboardingAPIView, BusinessOnboardingAPIView, PageOnboardingAPIView

urlpatterns = [
    path('user-onboard/', UserOnboardingAPIView.as_view(), name='user-onboard'),
    path('business-onboard/', BusinessOnboardingAPIView.as_view(), name='business-onboard'),
    path('page-onboard/', PageOnboardingAPIView.as_view(), name='page-onboard'),
]