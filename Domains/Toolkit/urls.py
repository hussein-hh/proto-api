from django.urls import path
from .views import WebMetricsAPIView

urlpatterns = [
    path('web-metrics/', WebMetricsAPIView.as_view(), name='web-metrics'),
]
