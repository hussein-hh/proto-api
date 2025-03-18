from django.urls import path
from Domains.Results.Views import UserUploadsSummaryAPIView

urlpatterns = [
    path('summarize/<int:file_id>/', UserUploadsSummaryAPIView.as_view(), name="get_user_uploads_summary"),
]