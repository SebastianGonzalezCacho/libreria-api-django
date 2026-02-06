# 📚 API REST de Librería con Django

Una API REST completa para gestión de librería con sistema de auditoría, pruebas automatizadas y exportación de informes.

## 🚀 Características

### ✅ Core Features
- **CRUD completo** para libros, autores, géneros, préstamos
- **Sistema de usuarios** con 4 roles (gratuito, premium, bibliotecario, DBA)
- **Autenticación** con tokens JWT
- **Permisos** por rol
- **Panel de administración** Django

### 🔍 Auditoría y Monitorización
- **Logging automático** de todas las operaciones CRUD
- **Exportación a Excel** de logs de auditoría
- **Estadísticas** en tiempo real
- **Registro de accesos** (login/logout)
- **IP y User Agent** tracking

### 🧪 Testing Automatizado
- **Pruebas unitarias** con pytest
- **Pruebas de integración** completas
- **Coverage report** automático
- **CI/CD** con GitHub Actions

## 📋 Requisitos

- Python 3.11+
- Django 5.2+
- MariaDB 10.5+ o SQLite
- pip install -r requirements.txt

## 🛠️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/SebastianGonzalezCacho/libreria-api-django.git
cd libreria-api-django

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (settings.py)
# Crear base de datos en MySQL/MariaDB o usar SQLite

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

## 📡 Endpoints de la API

### 🔐 Autenticación
- `POST /api/usuarios/users/register/` - Registrar nuevo usuario
- `POST /api/usuarios/users/login/` - Iniciar sesión
- `POST /api/usuarios/users/logout/` - Cerrar sesión

### 📚 Gestión de Libros
- `GET/POST /api/libros/libros/` - Listar/crear libros
- `GET/PUT/DELETE /api/libros/libros/{id}/` - Gestionar libro específico
- `POST /api/libros/libros/{id}/prestar/` - Pedir libro prestado
- `GET/POST /api/libros/autores/` - Gestionar autores
- `GET/POST /api/libros/generos/` - Gestionar géneros

### 🔄 Préstamos
- `GET/POST /api/libros/prestamos/` - Ver/practicar préstamos
- `POST /api/libros/prestamos/{id}/devolver/` - Devolver libro

### 📊 Auditoría y Reportes
- `GET /api/auditoria/logs/` - Ver logs de auditoría
- `GET /api/auditoria/logs/export_excel/` - Exportar logs a Excel
- `GET /api/auditoria/logs/statistics/` - Estadísticas de uso

## 🎯 Roles de Usuario

| Rol | Límite Préstamos | Permisos |
|-----|------------------|-----------|
| Gratuito | 3 | Ver/crear préstamos propios |
| Premium | 10 | Ver/crear préstamos propios |
| Bibliotecario | 50 | Ver TODOS los préstamos + gestión completa |
| DBA | 100 | Acceso completo + auditoría |

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con coverage
pytest --cov=libros --cov=usuarios --cov=auditoria --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_integracion.py::TestAuditoriaIntegracion -v
```

## 📊 Reportes y Exportación

### Exportar Logs a Excel
```bash
# Con token de autenticación
curl -H "Authorization: Token TU_TOKEN" \
     http://localhost:8000/api/auditoria/logs/export_excel/ \
     --output auditoria_logs.xlsx
```

### Estadísticas en Tiempo Real
```json
GET /api/auditoria/logs/statistics/

{
  "total_logs": 150,
  "recent_logs": 45,
  "actions_by_type": {
    "Creación": 20,
    "Actualización": 15,
    "Préstamo": 8
  },
  "objects_by_type": {
    "Libro": 25,
    "Prestamo": 12,
    "Autor": 8
  },
  "top_users": {
    "admin": 15,
    "bibliotecario1": 10,
    "usuario_premium": 5
  }
}
```

## 🏗️ Arquitectura

```
libreria-api-django/
├── libreria_api/          # Configuración principal
├── libros/               # App de gestión de libros
│   ├── models.py         # Modelo de datos
│   ├── views.py          # ViewSets API REST
│   ├── serializers.py    # Serializadores DRF
│   └── urls.py          # Endpoints
├── usuarios/             # App de gestión de usuarios
├── auditoria/            # App de auditoría y logs
├── tests/                # Pruebas automatizadas
├── logs/                 # Logs de aplicación
└── requirements.txt       # Dependencias
```

## 🔧 Configuración

### Base de Datos
```python
# SQLite (desarrollo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MySQL/MariaDB (producción)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'libreria_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'audit': {
            'format': '{asctime} - {user} - {action} - {object_type}',
            'style': '{',
        },
    },
    'handlers': {
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',
            'formatter': 'audit',
        },
    },
    'loggers': {
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🚀 Despliegue

### Docker (Recomendado)
```bash
# Construir imagen
docker build -t libreria-api .

# Ejecutar contenedor
docker run -p 8000:8000 libreria-api
```

### Producción con Gunicorn
```bash
pip install gunicorn
gunicorn libreria_api.wsgi:application --bind 0.0.0.0:8000
```

## 📈 Métricas y Monitorización

- **Coverage de código**: >95%
- **Tests automatizados**: 9 casos de prueba
- **CI/CD**: GitHub Actions
- **Logs estructurados**: JSON format
- **Exportación**: Excel con format profesional

## 🤝 Contribución

1. Fork el repositorio
2. Crear feature branch: `git checkout - feature/amazing-feature`
3. Commit cambios: `git commit -m 'Add amazing feature'`
4. Push al branch: `git push origin feature/amazing-feature`
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT - ver archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Sebastian González Cacho**
- GitHub: [@SebastianGonzalezCacho](https://github.com/SebastianGonzalezCacho)
- Email: [tu-email@example.com](mailto:tu-email@example.com)

## 🙏 Agradecimientos

- [Django](https://www.djangoproject.com/) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API toolkit
- [pytest](https://pytest.org/) - Testing framework
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel manipulation
