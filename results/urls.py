from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResultsListView.as_view(), name='results_list'),
]