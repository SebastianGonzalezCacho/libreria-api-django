import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from libros.models import Autor, Libro, Genero
from usuarios.models import PerfilUsuario
from django.urls import reverse
import json

@pytest.mark.django_db
class TestAuditoriaIntegracion(APITestCase):
    """Pruebas de integración para el sistema de auditoría"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.perfil = PerfilUsuario.objects.create(
            user=self.user,
            tipo_usuario='premium'
        )
        
        # Login y obtener token
        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        
        # Crear datos de prueba
        self.autor = Autor.objects.create(
            nombre='Gabriel',
            apellido='García Márquez'
        )
        self.genero = Genero.objects.create(nombre='Novela')
        
        self.libro_data = {
            'titulo': 'Cien años de soledad',
            'autor': self.autor.id,
            'genero': self.genero.id,
            'isbn': '9780307350454',
            'anio_publicacion': 1967,
            'editorial': 'Editorial Sudamericana',
            'num_paginas': 471,
            'idioma': 'Español',
            'descripcion': 'Una obra maestra de la literatura latinoamericana'
        }
    
    def test_creacion_libro_genera_audit_log(self):
        """Test: Crear libro genera log de auditoría"""
        from auditoria.models import AuditLog
        initial_logs = AuditLog.objects.count()
        
        response = self.client.post('/api/libros/libros/', self.libro_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        final_logs = AuditLog.objects.count()
        self.assertEqual(final_logs, initial_logs + 1)
        
        # Verificar que el log es correcto
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.object_type, 'Libro')
        self.assertEqual(log.user, self.user)
    
    def test_actualizacion_libro_genera_audit_log(self):
        """Test: Actualizar libro genera log de auditoría"""
        # Primero crear un libro
        libro = Libro.objects.create(**self.libro_data)
        
        from auditoria.models import AuditLog
        initial_logs = AuditLog.objects.count()
        
        # Actualizar libro
        update_data = {'titulo': 'Cien años de soledad (Edición Especial)'}
        response = self.client.patch(f'/api/libros/libros/{libro.id}/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar log de actualización
        log = AuditLog.objects.filter(action='UPDATE').latest('timestamp')
        self.assertIn('titulo', log.changes)
        self.assertEqual(log.changes['titulo']['old'], 'Cien años de soledad')
        self.assertEqual(log.changes['titulo']['new'], 'Cien años de soledad (Edición Especial)')
    
    def test_eliminacion_libro_genera_audit_log(self):
        """Test: Eliminar libro genera log de auditoría"""
        # Crear libro
        libro = Libro.objects.create(**self.libro_data)
        
        from auditoria.models import AuditLog
        initial_logs = AuditLog.objects.count()
        
        # Eliminar libro
        response = self.client.delete(f'/api/libros/libros/{libro.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar log de eliminación
        log = AuditLog.objects.filter(action='DELETE').latest('timestamp')
        self.assertEqual(log.object_id, libro.id)
        self.assertEqual(log.changes['deleted'], True)
    
    def test_prestamo_libro_genera_audit_log(self):
        """Test: Prestar libro genera log de auditoría"""
        from auditoria.models import AuditLog
        
        # Crear libro disponible
        libro = Libro.objects.create(**self.libro_data)
        initial_logs = AuditLog.objects.count()
        
        # Prestar libro
        prestamo_data = {
            'libro': libro.id,
            'fecha_devolucion': '2024-12-31'
        }
        response = self.client.post(f'/api/libros/libros/{libro.id}/prestar/', prestamo_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que se generó el log
        final_logs = AuditLog.objects.count()
        self.assertGreater(final_logs, initial_logs)
    
    def test_exportacion_excel_logs(self):
        """Test: Exportar logs a Excel"""
        # Crear algunos datos para exportar
        Libro.objects.create(**self.libro_data)
        
        response = self.client.get('/api/auditoria/logs/export_excel/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    def test_estadisticas_auditoria(self):
        """Test: Obtener estadísticas de auditoría"""
        # Crear datos de prueba
        Libro.objects.create(**self.libro_data)
        Autor.objects.create(nombre='Julio', apellido='Cortázar')
        
        response = self.client.get('/api/auditoria/logs/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_logs', response.data)
        self.assertIn('recent_logs', response.data)
        self.assertIn('actions_by_type', response.data)
        self.assertIn('objects_by_type', response.data)
        self.assertIn('top_users', response.data)

@pytest.mark.django_db
class TestEndpointsUsuarios(APITestCase):
    """Pruebas para endpoints de usuarios"""
    
    def test_registro_usuario(self):
        """Test: Registro de nuevo usuario"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'perfil': {
                'tipo_usuario': 'gratuito',
                'telefono': '1234567890'
            }
        }
        
        response = self.client.post('/api/usuarios/users/register/', user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        
        # Verificar que se creó el perfil
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertEqual(user.perfil.tipo_usuario, 'gratuito')
    
    def test_login_usuario(self):
        """Test: Inicio de sesión"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        PerfilUsuario.objects.create(
            user=user,
            tipo_usuario='premium'
        )
        
        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('perfil', response.data)

@pytest.mark.django_db
class TestEndpointsLibros(APITestCase):
    """Pruebas para endpoints de libros"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        PerfilUsuario.objects.create(
            user=self.user,
            tipo_usuario='premium'
        )
        
        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
    
    def test_crud_libro_completo(self):
        """Test: CRUD completo de libros"""
        # Crear autor y género
        autor = Autor.objects.create(nombre='Test', apellido='Author')
        genero = Genero.objects.create(nombre='Fiction')
        
        # CREATE
        libro_data = {
            'titulo': 'Test Book',
            'autor': autor.id,
            'genero': genero.id,
            'isbn': '1234567890123',
            'anio_publicacion': 2023,
            'idioma': 'Español'
        }
        response = self.client.post('/api/libros/libros/', libro_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        libro_id = response.data['id']
        
        # READ
        response = self.client.get('/api/libros/libros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # UPDATE
        update_data = {'titulo': 'Test Book (Updated)'}
        response = self.client.patch(f'/api/libros/libros/{libro_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Test Book (Updated)')
        
        # DELETE
        response = self.client.delete(f'/api/libros/libros/{libro_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)