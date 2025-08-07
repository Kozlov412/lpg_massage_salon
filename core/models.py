from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    """Абстрактная модель с полями created и updated"""
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Client(TimeStampedModel):
    """Модель клиента салона"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


