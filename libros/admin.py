from django.contrib import admin
from .models import Autor, Genero, Libro, Prestamo

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'nacionalidad')
    search_fields = ('nombre', 'apellido')
    list_filter = ('nacionalidad',)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'isbn', 'anio_publicacion', 'estado')
    search_fields = ('titulo', 'autor__nombre', 'autor__apellido')
    list_filter = ('genero', 'estado', 'idioma')
    date_hierarchy = 'fecha_creacion'

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('libro', 'usuario', 'fecha_prestamo', 'fecha_devolucion', 'estado')
    search_fields = ('libro__titulo', 'usuario__username')
    list_filter = ('estado', 'fecha_prestamo')
    date_hierarchy = 'fecha_prestamo'
