from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    date_hierarchy = 'created'