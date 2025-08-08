from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.calendar_settings_view, name='calendar_settings'),
    path('google/auth/', views.google_auth_init, name='google_auth_init'),
    path('google/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('google/remove/', views.remove_google_auth, name='remove_google_auth'),
    path('ical/download/<int:appointment_id>/', views.download_ical, name='download_ical'),
]