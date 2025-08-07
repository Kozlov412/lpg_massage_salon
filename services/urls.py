from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServiceCategoryListView.as_view(), name='service_categories'),
    path('category/<int:category_id>/', views.ServiceListView.as_view(), name='service_list'),
    path('detail/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
]