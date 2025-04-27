from django.urls import path
from .views import WebMetricsAPIView, PageHTMLAPIView, PageCSSAPIView, RoleModelWebMetricsAPIView, UserPagesView, TakeScreenshotAPIView, QuickChartAPIView

urlpatterns = [
    path('web-metrics/role-model/', RoleModelWebMetricsAPIView.as_view(), name='web-metrics'),
    path('web-metrics/business/', WebMetricsAPIView.as_view(), name='web-metrics'),
    path('business-html/', PageHTMLAPIView.as_view(), name='business-html'),
    path('business-css/', PageCSSAPIView.as_view(), name='business-css'),
    path('user-pages/', UserPagesView.as_view(), name='user-pages'),
    path('take-screenshot/', TakeScreenshotAPIView.as_view(), name='take-screenshot'),
    path('plot-chart/', QuickChartAPIView.as_view()),
]

