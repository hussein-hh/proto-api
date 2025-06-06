from django.urls import path
from .views import FileUploadView, FileListView, FileUpdateView, FileDeleteView, FileRetrieveView, FileShowView

urlpatterns = [
    path('create/', FileUploadView.as_view(), name='file-upload'),
    path('list/', FileListView.as_view(), name='file-list'), 
    path('update/<int:upload_id>/', FileUpdateView.as_view(), name='file-update'),
    path('delete/<int:upload_id>/', FileDeleteView.as_view(), name='file-delete'),
    path('retrieve/<int:upload_id>/', FileRetrieveView.as_view(), name='file-retireve'),
    path('show/<int:upload_id>/', FileShowView.as_view(), name='file-show'),
    
]
