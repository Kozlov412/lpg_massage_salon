from django.db import models
from core.models import TimeStampedModel

class Location(TimeStampedModel):
    """Модель филиала салона"""
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    working_hours = models.CharField(max_length=100, verbose_name="Часы работы")
    description = models.TextField(verbose_name="Описание", blank=True)
    image = models.ImageField(upload_to='locations/', verbose_name="Фото", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    latitude = models.CharField(max_length=20, verbose_name="Широта", blank=True, default="53.2007")
    longitude = models.CharField(max_length=20, verbose_name="Долгота", blank=True, default="45.0046")
    
    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"
        
    def __str__(self):
        return self.name