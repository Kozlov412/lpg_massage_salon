from django.db import models
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from core.models import TimeStampedModel
from locations.models import Location

# Получение модели пользователя
User = get_user_model()

class ServiceCategory(TimeStampedModel):
    """Категория услуг"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    image = models.ImageField(upload_to='categories/', verbose_name="Изображение", blank=True)
    icon = models.CharField(max_length=50, verbose_name="Bootstrap иконка", 
                          blank=True, help_text="Название иконки Bootstrap, например: 'bi-spa'")
    
    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        
    def __str__(self):
        return self.name

class Service(TimeStampedModel):
    """Модель услуги"""
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration = models.DurationField(verbose_name="Длительность")
    image = models.ImageField(upload_to='services/', verbose_name="Изображение", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        
    def __str__(self):
        return self.name

class ServiceReview(TimeStampedModel):
    """Модель отзыва об услуге"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews', verbose_name="Пользователь")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews', verbose_name="Услуга")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='service_reviews', verbose_name="Филиал")
    rating = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(verbose_name="Комментарий")
    is_published = models.BooleanField(verbose_name="Опубликован", default=True)
    
    class Meta:
        verbose_name = "Отзыв об услуге"
        verbose_name_plural = "Отзывы об услугах"
        ordering = ['-created']
        
    def __str__(self):
        return f"Отзыв на {self.service.name} от {self.user.get_full_name() or self.user.username}"
    
    def get_stars_display(self):
    
        if self.rating is None:
            return format_html('<span class="text-muted">Нет оценки</span>')
    
        stars = '★' * self.rating + '☆' * (5 - self.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)