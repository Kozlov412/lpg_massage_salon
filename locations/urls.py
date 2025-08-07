from django.urls import path
from . import views

urlpatterns = [
    path('', views.LocationListView.as_view(), name='location_list'),
    path('<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
]