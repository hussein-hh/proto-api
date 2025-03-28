from django.urls import path
from Domains.Results.Views import JobsAgent, ZahraAgent, DavinciAgentAPIView, EinsteinAgentAPIView

urlpatterns = [
    path('Jobs/', JobsAgent.as_view(), name="get_user_uploads_summary"),
    path('Zahra', ZahraAgent.as_view(), name="get_web_metrics"),
    path('davinci/', DavinciAgentAPIView.as_view(), name="davinci-agent"),
    path('einstein/', EinsteinAgentAPIView.as_view(), name="einstein-agent"),
]