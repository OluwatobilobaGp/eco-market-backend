from django.contrib import admin

from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'price', 'is_available', 'updated_at']
    list_editable = ['is_available', 'price']
    list_filter = ['is_available']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
