from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_repr', 'ip_address')
    list_filter = ('action', 'object_type', 'timestamp', 'user')
    search_fields = ('user__username', 'object_repr', 'changes')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'changes', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        return False  # No permitir crear logs manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar logs