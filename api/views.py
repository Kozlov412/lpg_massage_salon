from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from services.models import Service, ServiceCategory, ServiceReview
from locations.models import Location
from appointments.models import Appointment, Review
from django.shortcuts import get_object_or_404

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Разрешение доступа только владельцу объекта или администратору.
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем наличие атрибута client (для Appointment) или user (для Review)
        if hasattr(obj, 'client'):
            return obj.client == request.user or request.user.is_staff
        elif hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        elif hasattr(obj, 'appointment'):
            return obj.appointment.client == request.user or request.user.is_staff
        return request.user.is_staff

class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра категорий услуг.
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра услуг.
    """
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Получить отзывы о конкретной услуге.
        """
        service = self.get_object()
        reviews = ServiceReview.objects.filter(service=service, is_published=True)
        serializer = ServiceReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра филиалов.
    """
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address']

class ServiceReviewViewSet(viewsets.ModelViewSet):
    """
    API для просмотра и создания отзывов об услугах.
    """
    serializer_class = ServiceReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'location', 'rating', 'is_published']
    ordering_fields = ['created', 'rating']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ServiceReview.objects.all()
        return ServiceReview.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_published=False)

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API для управления записями на процедуры.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'location', 'status', 'date']
    ordering_fields = ['date', 'time', 'created']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(client=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user, status='pending')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отменить запись
        """
        appointment = self.get_object()
        if appointment.status in ['completed', 'canceled']:
            return Response(
                {"error": "Невозможно отменить завершенную или уже отмененную запись."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'canceled'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API для управления отзывами о процедурах.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['appointment', 'rating', 'is_published']
    ordering_fields = ['created', 'rating']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        
        # Для обычных пользователей отображаем либо их собственные отзывы, либо опубликованные
        return Review.objects.filter(
            appointment__client=self.request.user
        ) | Review.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        appointment = serializer.validated_data['appointment']
        
        # Проверка, что пользователь имеет право оставлять отзыв
        if appointment.client != self.request.user:
            return Response(
                {"error": "Вы можете оставлять отзывы только о своих записях."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверка, что процедура завершена
        if appointment.status != 'completed':
            return Response(
                {"error": "Можно оставлять отзывы только о завершенных процедурах."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка, что отзыв еще не оставлен
        if hasattr(appointment, 'review'):
            return Response(
                {"error": "Вы уже оставили отзыв об этой процедуре."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(is_published=False)
