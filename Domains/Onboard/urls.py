from django.urls import path
from .views import UserOnboardingAPIView, BusinessOnboardingAPIView, PageOnboardingAPIView, ScreenshotUploadAPIView

urlpatterns = [
    path('user-onboard/', UserOnboardingAPIView.as_view(), name='user-onboard'),
    path('business-onboard/', BusinessOnboardingAPIView.as_view(), name='business-onboard'),
    path('page-onboard/', PageOnboardingAPIView.as_view(), name='page-onboard'),
    path("upload-screenshot/", ScreenshotUploadAPIView.as_view(), name="upload-screenshot"),
]