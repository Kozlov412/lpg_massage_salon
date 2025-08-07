from django.db import models
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from core.models import TimeStampedModel
from locations.models import Location
from services.models import Service

User = get_user_model()

class Appointment(TimeStampedModel):
    """Модель записи на процедуру"""
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name="Клиент")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments', verbose_name="Услуга")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='appointments', verbose_name="Филиал")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    notes = models.TextField(verbose_name="Примечания", blank=True)
    admin_notes = models.TextField(verbose_name="Заметки администратора", blank=True, 
                                help_text="Эти заметки видны только администраторам")
    notified = models.BooleanField(verbose_name="Клиент уведомлен", default=False)
    
    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ['-date', '-time']
        
    def __str__(self):
        return f"{self.client.get_full_name() or self.client.username} - {self.service.name} ({self.date})"
    
    def get_colored_status(self):
        """Возвращает статус с цветовой индикацией для админ-панели"""
        colors = {
            'pending': '#FFC107',   # Желтый
            'confirmed': '#28A745', # Зеленый
            'completed': '#17A2B8', # Голубой
            'canceled': '#DC3545',  # Красный
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>',
            colors.get(self.status, '#6C757D'),
            self.get_status_display()
        )
    get_colored_status.short_description = 'Статус'
    
    def client_full_name(self):
        """Возвращает полное имя клиента"""
        return self.client.get_full_name() or self.client.username
    client_full_name.short_description = 'Клиент'
    
    def client_phone(self):
        """Возвращает телефон клиента, если он есть"""
        try:
            return self.client.client.phone
        except:
            return "Не указан"
    client_phone.short_description = 'Телефон клиента'

class Review(TimeStampedModel):
    """Модель отзыва о процедуре"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, 
                                      related_name='review', verbose_name="Запись")
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(verbose_name="Комментарий")
    is_published = models.BooleanField(verbose_name="Опубликован", default=True)
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        
    def __str__(self):
        return f"Отзыв от {self.appointment.client.get_full_name() or self.appointment.client.username}"
    
    def service_name(self):
        return self.appointment.service.name
    service_name.short_description = 'Услуга'
    
    def location_name(self):
        return self.appointment.location.name
    location_name.short_description = 'Филиал'
    
    def get_stars_display(self):
        """Возвращает звездный рейтинг для админ-панели"""
        stars = '★' * self.rating + '☆' * (5 - self.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    get_stars_display.short_description = 'Рейтинг'
    
    def client_name(self):
        return self.appointment.client.get_full_name() or self.appointment.client.username
    client_name.short_description = 'Клиент'