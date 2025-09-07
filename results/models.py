from django.db import models
from services.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator

class BeforeAfterResult(models.Model):
    """Модель для хранения результатов 'До и После'"""
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='results', verbose_name="Процедура")
    before_image = models.ImageField(upload_to='results/before/', verbose_name="Фото 'До'")
    after_image = models.ImageField(upload_to='results/after/', verbose_name="Фото 'После'")
    sessions_count = models.PositiveIntegerField(
        verbose_name="Количество сеансов", 
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Сколько сеансов потребовалось для достижения результата"
    )
    period = models.CharField(
        max_length=100, 
        verbose_name="Период", 
        help_text="Например: '2 месяца', '6 недель'"
    )
    description = models.TextField(verbose_name="Описание результата", blank=True)
    client_gender = models.CharField(
        max_length=10,
        choices=[('male', 'Мужчина'), ('female', 'Женщина')],
        verbose_name="Пол клиента",
        default='female'
    )
    client_age = models.PositiveIntegerField(
        verbose_name="Возраст клиента",
        validators=[MinValueValidator(18), MaxValueValidator(100)],
        null=True, blank=True
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Результат До/После"
        verbose_name_plural = "Результаты До/После"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.service.name}"


