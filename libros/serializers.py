from rest_framework import serializers
from .models import Autor, Genero, Libro, Prestamo
from django.contrib.auth.models import User

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

class LibroSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.__str__', read_only=True)
    genero_nombre = serializers.CharField(source='genero.nombre', read_only=True)
    
    class Meta:
        model = Libro
        fields = '__all__'

class PrestamoSerializer(serializers.ModelSerializer):
    libro_titulo = serializers.CharField(source='libro.titulo', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Prestamo
        fields = '__all__'

class PrestamoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        fields = ['libro', 'fecha_devolucion', 'observaciones']