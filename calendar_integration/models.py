from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GoogleCalendarCredentials(models.Model):
    """Модель для хранения учетных данных Google Calendar"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_calendar')
    token = models.JSONField(verbose_name="Токен доступа")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Учетные данные Google Calendar"
        verbose_name_plural = "Учетные данные Google Calendar"
    
    def __str__(self):
        return f"Google Calendar - {self.user.username}"

class CalendarSettings(models.Model):
    """Настройки интеграции с календарями для пользователя"""
    CALENDAR_CHOICES = (
        ('none', 'Не использовать'),
        ('google', 'Google Calendar'),
        ('ical', 'iCalendar (Apple, Outlook и др.)'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar_settings')
    calendar_type = models.CharField(max_length=10, choices=CALENDAR_CHOICES, default='none', 
                                    verbose_name="Тип календаря")
    add_appointments = models.BooleanField(default=True, verbose_name="Добавлять новые записи в календарь")
    update_appointments = models.BooleanField(default=True, verbose_name="Обновлять измененные записи в календаре")
    remove_canceled = models.BooleanField(default=True, verbose_name="Удалять отмененные записи из календаря")
    reminder_time = models.IntegerField(default=60, verbose_name="Время напоминания (в минутах)")
    
    class Meta:
        verbose_name = "Настройки календаря"
        verbose_name_plural = "Настройки календарей"
    
    def __str__(self):
        return f"Настройки календаря - {self.user.username}"


