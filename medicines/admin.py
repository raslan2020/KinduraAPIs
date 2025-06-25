from django.contrib import admin
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    """
    Admin for Medicine model
    """
    list_display = ['name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'name', 'description')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
