from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('list/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('<int:appointment_id>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    
    # Административные URL-пути
    path('admin/list/', views.AdminAppointmentListView.as_view(), name='admin_appointment_list'),
    path('admin/<int:pk>/', views.AdminAppointmentDetailView.as_view(), name='admin_appointment_detail'),
    path('admin/<int:pk>/update/', views.AdminAppointmentUpdateView.as_view(), name='admin_appointment_update'),
    path('admin/reviews/', views.AdminReviewListView.as_view(), name='admin_review_list'),
    path('admin/reviews/<int:pk>/', views.AdminReviewDetailView.as_view(), name='admin_review_update'),
]