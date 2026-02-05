from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Autor, Genero, Libro, Prestamo
from .serializers import (
    AutorSerializer, GeneroSerializer, LibroSerializer, 
    PrestamoSerializer, PrestamoCreateSerializer
)

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    permission_classes = [permissions.IsAuthenticated]

class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    permission_classes = [permissions.IsAuthenticated]

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def prestar(self, request, pk=None):
        libro = self.get_object()
        if libro.estado != 'disponible':
            return Response({'error': 'El libro no está disponible'}, status=status.HTTP_400_BAD_REQUEST)
        
        perfil = request.user.perfil
        if not perfil.puede_prestar():
            return Response({'error': 'Has alcanzado tu límite de préstamos'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PrestamoCreateSerializer(data=request.data)
        if serializer.is_valid():
            prestamo = serializer.save(libro=libro, usuario=request.user)
            libro.estado = 'prestado'
            libro.save()
            return Response(PrestamoSerializer(prestamo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.perfil.tipo_usuario in ['bibliotecario', 'dba']:
            return Prestamo.objects.all()
        return Prestamo.objects.filter(usuario=user)
    
    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        prestamo = self.get_object()
        if prestamo.usuario != request.user and request.user.perfil.tipo_usuario not in ['bibliotecario', 'dba']:
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        if prestamo.estado != 'activo':
            return Response({'error': 'El préstamo no está activo'}, status=status.HTTP_400_BAD_REQUEST)
        
        prestamo.estado = 'devuelto'
        prestamo.save()
        return Response({'message': 'Libro devuelto correctamente'})
