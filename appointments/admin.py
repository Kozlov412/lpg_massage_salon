from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import Appointment, Review

class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0
    readonly_fields = ('get_stars_display',)
    fields = ('rating', 'get_stars_display', 'comment', 'is_published', 'created')
    can_delete = False

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_full_name', 'service', 'location', 'date', 'time', 'get_colored_status', 'client_phone', 'has_review')
    list_filter = ('status', 'location', 'date', 'service__category')
    search_fields = ('client__username', 'client__first_name', 'client__last_name', 'client__client__phone')
    date_hierarchy = 'date'
    readonly_fields = ('created', 'updated', 'client_full_name', 'client_phone', 'get_colored_status')
    fieldsets = (
        ('Клиент', {
            'fields': ('client', 'client_full_name', 'client_phone')
        }),
        ('Запись', {
            'fields': ('service', 'location', 'date', 'time', 'status', 'get_colored_status')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'admin_notes', 'notified', 'created', 'updated')
        }),
    )
    inlines = [ReviewInline]
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_canceled', 'send_notification']
    
    def has_review(self, obj):
        """Проверяет, есть ли у записи отзыв"""
        has_review = hasattr(obj, 'review')
        if has_review:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_review.short_description = 'Отзыв'
    
    def mark_as_confirmed(self, request, queryset):
        """Отмечает выбранные записи как подтвержденные"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} записей отмечены как подтвержденные.")
    mark_as_confirmed.short_description = "Отметить как подтвержденные"
    
    def mark_as_completed(self, request, queryset):
        """Отмечает выбранные записи как завершенные"""
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} записей отмечены как завершенные.")
    mark_as_completed.short_description = "Отметить как завершенные"
    
    def mark_as_canceled(self, request, queryset):
        """Отмечает выбранные записи как отмененные"""
        updated = queryset.update(status='canceled')
        self.message_user(request, f"{updated} записей отмечены как отмененные.")
    mark_as_canceled.short_description = "Отметить как отмененные"
    
    def send_notification(self, request, queryset):
        """Отправляет уведомления клиентам о статусе заявок"""
        # В реальном проекте здесь будет код отправки email или SMS
        updated = queryset.update(notified=True)
        self.message_user(request, f"Отправлены уведомления для {updated} записей.")
    send_notification.short_description = "Отправить уведомления клиентам"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'service_name', 'location_name', 'get_stars_display', 'created', 'is_published')
    list_filter = ('rating', 'is_published', 'appointment__location', 'appointment__service__category')
    search_fields = ('appointment__client__username', 'appointment__client__first_name', 'appointment__client__last_name', 'comment')
    readonly_fields = ('get_stars_display', 'appointment_details', 'created', 'updated')
    fields = ('appointment', 'appointment_details', 'rating', 'get_stars_display', 'comment', 'is_published', 'created', 'updated')
    actions = ['publish_reviews', 'unpublish_reviews']
    
    def appointment_details(self, obj):
        """Отображает детали записи"""
        if not obj.appointment:
            return "-"
            
        client_name = obj.appointment.client.get_full_name() or obj.appointment.client.username
        return format_html(
            "<strong>Клиент:</strong> {}<br>"
            "<strong>Услуга:</strong> {}<br>"
            "<strong>Филиал:</strong> {}<br>"
            "<strong>Дата и время:</strong> {} в {}",
            client_name,
            obj.appointment.service.name,
            obj.appointment.location.name,
            obj.appointment.date,
            obj.appointment.time.strftime("%H:%M")
        )
    appointment_details.short_description = 'Детали записи'
    
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