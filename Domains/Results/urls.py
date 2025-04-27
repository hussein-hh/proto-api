from django.urls import path
from Domains.Results.Views import PageStructureAPIView, PageStylingAPIView, PageUIReportAPIView, EvaluateUIAPIView, EvaluateUBAAPIView, GenerateChartsAPIView, FormulateUIAPIView

urlpatterns = [
    path('describe-structure/', PageStructureAPIView.as_view(), name='describe-image'),
    path('describe-styling/', PageStylingAPIView.as_view(), name='describe_styling'),
    path('describe-page/', PageUIReportAPIView.as_view(), name='describe_page'),
    path('evaluate-ui/',        EvaluateUIAPIView.as_view(),   name='evaluate-ui'),
    path('evaluate-uba/', EvaluateUBAAPIView.as_view(), name='evaluate-uba'),
    path('generate-chart/', GenerateChartsAPIView.as_view(), name='generate-chart')
    path('formulate-ui/',      FormulateUIAPIView.as_view(),  name='formulate-ui'),
]