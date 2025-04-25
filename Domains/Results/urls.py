from django.urls import path
from Domains.Results.Views import PageStructureAPIView, PageStylingAPIView, PageUIReportAPIView, EvaluateUIAPIView

urlpatterns = [
    path('describe-structure/', PageStructureAPIView.as_view(), name='describe-image'),
    path('describe-styling/', PageStylingAPIView.as_view(), name='describe_styling'),
    path('describe-page/', PageUIReportAPIView.as_view(), name='describe_page'),
    path('evaluate-ui/',        EvaluateUIAPIView.as_view(),   name='evaluate-ui'),
]