from django.urls import path
from .views import UserOnboardingAPIView, BusinessOnboardingAPIView, PageOnboardingAPIView, ScreenshotUploadAPIView, PageDeleteAPIView

urlpatterns = [
    path('user-onboard/', UserOnboardingAPIView.as_view(), name='user-onboard'),
    path('business-onboard/', BusinessOnboardingAPIView.as_view(), name='business-onboard'),
    path('page-onboard/', PageOnboardingAPIView.as_view(), name='page-onboard'),
    path("upload-screenshot/", ScreenshotUploadAPIView.as_view(), name="upload-screenshot"),
    path('pages/<int:page_id>/<str:page_type>/',  PageDeleteAPIView.as_view(),   name='page-delete'),
]