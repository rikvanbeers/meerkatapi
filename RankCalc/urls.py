from django.urls import path
from RankCalc import views as views

urlpatterns = [
    path('rankresults/', views.RankResults.as_view(), name='rankresults'),
]
