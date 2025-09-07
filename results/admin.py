from django.contrib import admin
from django.utils.html import format_html
from .models import BeforeAfterResult

class BeforeAfterResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', 'sessions_count', 'period', 'display_before_image', 'display_after_image', 'is_published')
    list_filter = ('service', 'is_published', 'client_gender')
    search_fields = ('title', 'description', 'service__name')
    list_editable = ('is_published',)
    
    def display_before_image(self, obj):
        if obj.before_image:
            return format_html('<img src="{}" width="100" />', obj.before_image.url)
        return "Нет изображения"
    display_before_image.short_description = 'Фото "До"'
    
    def display_after_image(self, obj):
        if obj.after_image:
            return format_html('<img src="{}" width="100" />', obj.after_image.url)
        return "Нет изображения"
    display_after_image.short_description = 'Фото "После"'

admin.site.register(BeforeAfterResult, BeforeAfterResultAdmin)

# Register your models here.
