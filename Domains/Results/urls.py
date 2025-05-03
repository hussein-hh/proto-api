from django.urls import path
from Domains.Results.Views import PageStructureAPIView, PageStylingAPIView, PageUIReportAPIView, EvaluateUIAPIView, EvaluateUBAAPIView, FormulateUIAPIView, UBAProblemSolutionsAPIView, WebSearchAPIView

urlpatterns = [
    path('describe-structure/', PageStructureAPIView.as_view(), name='describe-image'),
    path('describe-styling/', PageStylingAPIView.as_view(), name='describe_styling'),
    path('describe-page/', PageUIReportAPIView.as_view(), name='describe_page'),
    path('evaluate-ui/',        EvaluateUIAPIView.as_view(),   name='evaluate-ui'),
    path('evaluate-uba/', EvaluateUBAAPIView.as_view(), name='evaluate-uba'),
    path('formulate-ui/',      FormulateUIAPIView.as_view(),  name='formulate-ui'),
    path('web-search/',      UBAProblemSolutionsAPIView.as_view(),  name='web-search'),
        path('webby-search/',      WebSearchAPIView.as_view(),  name='webby-search'),
]