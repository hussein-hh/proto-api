from django.urls import path
from Domains.Results.Views import UserUploadsSummaryAPIView, WebAgentAPIView, FeynmanAgentAPIView

urlpatterns = [
    path('summarize/', UserUploadsSummaryAPIView.as_view(), name="get_user_uploads_summary"),
    path('web-agent', WebAgentAPIView.as_view(), name="get_web_metrics"),
    path('feynman/', FeynmanAgentAPIView.as_view(), name="feynman_system_message"),
]