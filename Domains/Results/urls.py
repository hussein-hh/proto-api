from django.urls import path
from Domains.Results.Views import FeynmanAgentAPIView, ZahraAgent, DavinciAgentAPIView, EinsteinAgentAPIView, HusseinAgentAPIView, FeynmanAgentAPIView, JobsAgentAPIView, UltraAgentAPIView

urlpatterns = [
    path('Jobs/', JobsAgentAPIView.as_view(), name="get_user_uploads_summary"),
    path('feynman/', FeynmanAgentAPIView.as_view(), name="get_web_metrics"), 
    path('Zahra/', ZahraAgent.as_view(), name="get_web_metrics"),
    path('davinci/', DavinciAgentAPIView.as_view(), name="davinci-agent"),
    path('einstein/', EinsteinAgentAPIView.as_view(), name="einstein-agent"),
    path('hussein/', HusseinAgentAPIView.as_view(), name="hussein-agent"),
    path('ultra/', UltraAgentAPIView.as_view(), name="ultra-agent")
]