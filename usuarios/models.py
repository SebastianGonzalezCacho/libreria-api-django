from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('gratuito', 'Gratuito'),
        ('premium', 'Premium'),
        ('bibliotecario', 'Bibliotecario'),
        ('dba', 'DBA'),
    ]

    LIMITES_POR_ROL = {
        'gratuito': 3,
        'premium': 10,
        'bibliotecario': 50,
        'dba': 100,
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='gratuito')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    limite_prestamos = models.IntegerField(default=3)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

    def save(self, *args, **kwargs):
        # Sincronizar límite de préstamos según el rol
        self.limite_prestamos = self.LIMITES_POR_ROL.get(self.tipo_usuario, 3)
        super().save(*args, **kwargs)

    def puede_prestar(self):
        prestamos_activos = self.user.prestamos.filter(estado='activo').count()
        return prestamos_activos < self.limite_prestamos
