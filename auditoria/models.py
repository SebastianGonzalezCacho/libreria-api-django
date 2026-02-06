from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json
import logging

logger = logging.getLogger('audit')

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('PRESTAMO', 'Préstamo'),
        ('DEVOLUCION', 'Devolución'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_type} - {self.timestamp}"

def create_audit_log(sender, instance, action, **kwargs):
    """Función helper para crear logs de auditoría"""
    try:
        if sender == AuditLog or sender._meta.label in ['auth.Permission', 'contenttypes.ContentType', 'sessions.Session']:
            return
        
        # Solo auditar modelos importantes
        important_models = ['Libro', 'Autor', 'Genero', 'Prestamo', 'PerfilUsuario', 'User']
        model_name = sender.__name__
        
        if model_name not in important_models:
            return
        
        changes = {}
        if action == 'UPDATE':
            try:
                # Obtener el estado anterior si existe
                if hasattr(instance, '_state') and instance._state.db:
                    old_instance = sender.objects.get(pk=instance.pk)
                    for field in instance._meta.fields:
                        field_name = field.name
                        old_value = getattr(old_instance, field_name)
                        new_value = getattr(instance, field_name)
                        if old_value != new_value:
                            changes[field_name] = {
                                'old': str(old_value),
                                'new': str(new_value)
                            }
            except (sender.DoesNotExist, AttributeError):
                pass
        elif action == 'CREATE':
            changes = {'created': True}
        elif action == 'DELETE':
            changes = {'deleted': True}
        
        AuditLog.objects.create(
            user=getattr(instance, 'user', None) if hasattr(instance, 'user') else None,
            action=action,
            object_type=model_name,
            object_id=instance.pk,
            object_repr=str(instance)[:200],
            changes=changes
        )
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Registrar cambios CREATE/UPDATE"""
    action = 'CREATE' if created else 'UPDATE'
    create_audit_log(sender, instance, action)

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Registrar eliminaciones DELETE"""
    create_audit_log(sender, instance, 'DELETE')