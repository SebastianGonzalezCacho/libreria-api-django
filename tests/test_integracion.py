import pytest
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from libros.models import Autor, Libro, Genero
from usuarios.models import PerfilUsuario


@pytest.mark.django_db
class TestAuditoriaIntegracion(APITestCase):
    """Pruebas de integración para el sistema de auditoría"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        PerfilUsuario.objects.create(user=self.user, tipo_usuario='premium')

        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        self.autor = Autor.objects.create(nombre='Gabriel', apellido='García Márquez')
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
            'descripcion': 'Una obra maestra de la literatura latinoamericana',
        }

    def test_creacion_libro_genera_audit_log(self):
        from auditoria.models import AuditLog
        initial_logs = AuditLog.objects.count()

        response = self.client.post('/api/libros/libros/', self.libro_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AuditLog.objects.count(), initial_logs + 1)

        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.object_type, 'Libro')

    def test_actualizacion_libro_genera_audit_log(self):
        libro = Libro.objects.create(**{
            'titulo': 'Cien años de soledad',
            'autor': self.autor,
            'genero': self.genero,
            'isbn': '9780307350454',
            'anio_publicacion': 1967,
        })

        response = self.client.patch(
            f'/api/libros/libros/{libro.id}/',
            {'titulo': 'Cien años de soledad (Edición Especial)'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        from auditoria.models import AuditLog
        log = AuditLog.objects.filter(action='UPDATE').latest('timestamp')
        self.assertIn('titulo', log.changes)
        self.assertEqual(log.changes['titulo']['old'], 'Cien años de soledad')
        self.assertEqual(log.changes['titulo']['new'], 'Cien años de soledad (Edición Especial)')

    def test_eliminacion_libro_genera_audit_log(self):
        libro = Libro.objects.create(**{
            'titulo': 'Cien años de soledad',
            'autor': self.autor,
            'genero': self.genero,
            'isbn': '9780307350454',
            'anio_publicacion': 1967,
        })

        response = self.client.delete(f'/api/libros/libros/{libro.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        from auditoria.models import AuditLog
        log = AuditLog.objects.filter(action='DELETE').latest('timestamp')
        self.assertEqual(log.object_id, libro.id)
        self.assertTrue(log.changes.get('deleted'))

    def test_exportacion_excel_logs(self):
        Libro.objects.create(**{
            'titulo': 'Cien años de soledad',
            'autor': self.autor,
            'genero': self.genero,
            'isbn': '9780307350454',
            'anio_publicacion': 1967,
        })

        response = self.client.get('/api/auditoria/logs/export_excel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_estadisticas_auditoria(self):
        Libro.objects.create(**{
            'titulo': 'Cien años de soledad',
            'autor': self.autor,
            'genero': self.genero,
            'isbn': '9780307350454',
            'anio_publicacion': 1967,
        })

        response = self.client.get('/api/auditoria/logs/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ('total_logs', 'recent_logs', 'actions_by_type', 'objects_by_type', 'top_users'):
            self.assertIn(key, response.data)


@pytest.mark.django_db
class TestEndpointsUsuarios(APITestCase):

    def test_registro_usuario(self):
        response = self.client.post('/api/usuarios/users/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')

        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'perfil'))

    def test_login_usuario(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        PerfilUsuario.objects.create(user=user, tipo_usuario='premium')

        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('perfil', response.data)


@pytest.mark.django_db
class TestEndpointsLibros(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        PerfilUsuario.objects.create(user=self.user, tipo_usuario='premium')

        response = self.client.post('/api/usuarios/users/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test_crud_libro_completo(self):
        autor = Autor.objects.create(nombre='Test', apellido='Author')
        genero = Genero.objects.create(nombre='Fiction')

        # CREATE
        response = self.client.post('/api/libros/libros/', {
            'titulo': 'Test Book',
            'autor': autor.id,
            'genero': genero.id,
            'isbn': '1234567890123',
            'anio_publicacion': 2023,
            'idioma': 'Español',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        libro_id = response.data['id']

        # READ
        response = self.client.get('/api/libros/libros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

        # UPDATE
        response = self.client.patch(f'/api/libros/libros/{libro_id}/', {'titulo': 'Test Book (Updated)'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Test Book (Updated)')

        # DELETE
        response = self.client.delete(f'/api/libros/libros/{libro_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
