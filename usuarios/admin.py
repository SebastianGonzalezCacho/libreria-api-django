from django.contrib import admin
from .models import PerfilUsuario
from django.contrib.auth.models import User

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'telefono', 'fecha_registro', 'activo')
    search_fields = ('user__username', 'user__email')
    list_filter = ('tipo_usuario', 'activo', 'fecha_registro')
    date_hierarchy = 'fecha_registro'
