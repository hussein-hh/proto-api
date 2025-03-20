from django.urls import path
from Domains.Results.Views import UserUploadsSummaryAPIView

urlpatterns = [
    path('summarize/', UserUploadsSummaryAPIView.as_view(), name="get_user_uploads_summary"),
]