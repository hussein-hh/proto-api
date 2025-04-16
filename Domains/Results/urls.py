from django.urls import path
from Domains.Results.Views import ImageCaptionAPIView

urlpatterns = [
    path('describe-image/', ImageCaptionAPIView.as_view(), name='describe-image'),
]