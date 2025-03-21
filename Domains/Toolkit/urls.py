from django.urls import path
from .views import WebMetricsAPIView

urlpatterns = [
    path('web-metrics/role-model/', WebMetricsAPIView.as_view(), name='web-metrics'),
    path('web-metrics/business/', WebMetricsAPIView.as_view(), name='web-metrics'),
]
