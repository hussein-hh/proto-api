from django.urls import path
from .views import SignupView, LoginView, ChangeEmailAPIView, ChangePasswordAPIView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-email/', ChangeEmailAPIView.as_view(), name='change_email'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
]
