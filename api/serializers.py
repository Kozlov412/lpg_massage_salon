from rest_framework import serializers
from services.models import Service, ServiceCategory, ServiceReview
from locations.models import Location
from appointments.models import Appointment, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'phone', 'email', 'working_hours', 'description', 'is_active']

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'image', 'icon']

class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        write_only=True,
        source='category'
    )
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'image', 'is_active', 'category', 'category_id']

class ServiceReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        write_only=True,
        source='service'
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        source='location'
    )
    
    class Meta:
        model = ServiceReview
        fields = ['id', 'user', 'service', 'service_id', 'location', 'location_id', 'rating', 'comment', 'is_published', 'created', 'modified']
        read_only_fields = ['is_published', 'created', 'modified']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AppointmentSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        write_only=True,
        source='service'
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        source='location'
    )
    
    class Meta:
        model = Appointment
        fields = ['id', 'client', 'service', 'service_id', 'location', 'location_id', 'date', 'time', 'status', 'notes', 'created', 'modified']
        read_only_fields = ['status', 'created', 'modified']
    
    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        write_only=True,
        source='appointment'
    )
    
    class Meta:
        model = Review
        fields = ['id', 'appointment', 'appointment_id', 'rating', 'comment', 'is_published', 'created', 'modified']
        read_only_fields = ['is_published', 'created', 'modified']
    
    def validate_appointment_id(self, value):
        # Проверяем, что заявка принадлежит текущему пользователю и имеет статус "completed"
        if value.client != self.context['request'].user:
            raise serializers.ValidationError("Вы можете оставлять отзывы только о своих записях.")
        if value.status != 'completed':
            raise serializers.ValidationError("Можно оставлять отзывы только о завершенных процедурах.")
        return value