from django.urls import path
from .views import WebMetricsAPIView, BusinessHTMLAPIView, BusinessCSSAPIView

urlpatterns = [
    path('web-metrics/role-model/', WebMetricsAPIView.as_view(), name='web-metrics'),
    path('web-metrics/business/', WebMetricsAPIView.as_view(), name='web-metrics'),
    path('business-html/', BusinessHTMLAPIView.as_view(), name='business-html'),
    path('business-css/', BusinessCSSAPIView.as_view(), name='business-css'),


]
