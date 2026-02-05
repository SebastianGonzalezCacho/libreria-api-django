from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
    
    def __str__(self):
        return self.nombre

class Libro(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('mantenimiento', 'En Mantenimiento'),
        ('baja', 'Dado de Baja'),
    ]
    
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros')
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, related_name='libros')
    isbn = models.CharField(max_length=13, unique=True)
    anio_publicacion = models.IntegerField()
    editorial = models.CharField(max_length=100, blank=True, null=True)
    num_paginas = models.IntegerField(blank=True, null=True)
    idioma = models.CharField(max_length=50, default='Español')
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateField()
    fecha_devuelto = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.username}"
    
    def save(self, *args, **kwargs):
        if self.estado == 'devuelto' and not self.fecha_devuelto:
            self.fecha_devuelto = timezone.now()
            self.libro.estado = 'disponible'
            self.libro.save()
        super().save(*args, **kwargs)
