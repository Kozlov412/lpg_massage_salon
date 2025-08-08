from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views

# Создание схемы документации API
schema_view = get_schema_view(
    openapi.Info(
        title="LPG Массаж API",
        default_version='v1',
        description="API для мобильного приложения салона LPG массажа",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Регистрация маршрутов
router = DefaultRouter()
router.register(r'categories', views.ServiceCategoryViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'service-reviews', views.ServiceReviewViewSet, basename='service-review')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # JWT Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('', include(router.urls)),
]