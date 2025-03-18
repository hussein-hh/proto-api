from django.urls import path
from Domains.Results.Views import get_user_uploads_summary

urlpatterns = [
    path('summarize/<int:user_id>/', get_user_uploads_summary, name="get_user_uploads_summary"),
]
