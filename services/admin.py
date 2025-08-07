from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, Service, ServiceReview

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')
    search_fields = ('name',)
    prepopulated_fields = {'icon': ('name',)}

class ServiceReviewInline(admin.TabularInline):
    model = ServiceReview
    extra = 0
    readonly_fields = ('get_stars_display', 'created')
    fields = ('user', 'location', 'rating', 'get_stars_display', 'comment', 'is_published', 'created')
    can_delete = True
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'is_active', 'average_rating_display')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('average_rating_display', 'review_count')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'price', 'duration')
        }),
        ('Дополнительно', {
            'fields': ('image', 'is_active', 'average_rating_display', 'review_count')
        }),
    )
    inlines = [ServiceReviewInline]
    
    def average_rating_display(self, obj):
        """Отображение среднего рейтинга услуги с звездочками"""
        avg_rating = ServiceReview.objects.filter(service=obj, is_published=True).values_list('rating', flat=True)
        if not avg_rating:
            return "Нет отзывов"
            
        avg = sum(avg_rating) / len(avg_rating)
        stars = '★' * int(avg) + '☆' * (5 - int(avg))
        return format_html('<span style="color: #FFD700;">{}</span> ({:.1f} из 5)', stars, avg)
    average_rating_display.short_description = "Средний рейтинг"
    
    def review_count(self, obj):
        """Возвращает количество отзывов для услуги"""
        return obj.reviews.filter(is_published=True).count()
    review_count.short_description = "Количество отзывов"

@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'location', 'get_stars_display', 'created', 'is_published')
    list_filter = ('rating', 'is_published', 'location', 'service__category')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'comment', 'service__name')
    readonly_fields = ('get_stars_display', 'created')
    actions = ['publish_reviews', 'unpublish_reviews']
    
    def publish_reviews(self, request, queryset):
        """Публикует выбранные отзывы"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} отзывов опубликовано.")
    publish_reviews.short_description = "Опубликовать выбранные отзывы"
    
    def unpublish_reviews(self, request, queryset):
        """Скрывает выбранные отзывы"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} отзывов скрыто.")
    unpublish_reviews.short_description = "Скрыть выбранные отзывы"