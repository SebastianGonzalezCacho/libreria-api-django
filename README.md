# 📚 API REST de Librería con Django

API REST para gestión de librería con sistema de auditoría, pruebas automatizadas y exportación de reportes.

## 🚀 Características

- **CRUD completo** para libros, autores, géneros y préstamos
- **Sistema de usuarios** con 4 roles (gratuito, premium, bibliotecario, DBA)
- **Autenticación** con tokens DRF (`TokenAuthentication`)
- **Permisos** por rol
- **Auditoría automática** de operaciones CRUD con exportación a Excel
- **Estadísticas** de uso en tiempo real
- **Pruebas automatizadas** con pytest y CI con GitHub Actions

## 📋 Requisitos

- Python 3.11+
- Django 5.2+
- MariaDB 10.5+ (o SQLite para desarrollo rápido sin instalar nada extra)
- Docker + Docker Compose (opcional, para levantar todo en contenedores)

## 🛠️ Instalación

### Opción A — Docker (recomendado)

Levanta la app y MariaDB con un solo comando, sin instalar Python ni la BD localmente.

```bash
# 1. Clonar repositorio
git clone https://github.com/SebastianGonzalezCacho/libreria-api-django.git
cd libreria-api-django

# 2. Crear archivo de configuración
cp .env.example .env
# En Windows: copy .env.example .env

# 3. Construir y levantar
docker compose up --build

# 4. Crear superusuario (en otra terminal, con los contenedores corriendo)
docker compose exec web python manage.py createsuperuser
```

La API queda disponible en `http://localhost:8000`.

### Opción B — Entorno virtual local con MariaDB

```bash
git clone https://github.com/SebastianGonzalezCacho/libreria-api-django.git
cd libreria-api-django

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# mysqlclient necesita librerías del sistema:
# Ubuntu/Debian: sudo apt install default-libmysqlclient-dev pkg-config gcc
# Windows: instalar MySQL Connector/C desde mysql.com
pip install -r requirements.txt

cp .env.example .env
# Editar .env con los datos de tu base de datos local

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Opción C — SQLite (desarrollo rápido, sin instalar BD)

En el archivo `.env`, pon `USE_SQLITE=True`. El resto de variables `DB_*` se ignorarán.

```bash
# En .env:
USE_SQLITE=True
SECRET_KEY=cualquier-clave-larga
DEBUG=True
```

## ⚙️ Variables de entorno

Copia `.env.example` como `.env` y ajusta los valores:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django (¡cámbiala!) | — |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma | `localhost,127.0.0.1` |
| `USE_SQLITE` | Usar SQLite en lugar de MariaDB | `False` |
| `DB_NAME` | Nombre de la base de datos | `libreria_db` |
| `DB_USER` | Usuario de la BD | `libreria_user` |
| `DB_PASSWORD` | Contraseña de la BD | — |
| `DB_HOST` | Host de la BD (usar `db` con Docker) | `localhost` |
| `DB_PORT` | Puerto de la BD | `3306` |

## 📡 Endpoints de la API

### 🔐 Autenticación

La API usa **Token Authentication** de DRF. Incluye el token en cada request:

```
Authorization: Token <tu_token>
```

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/usuarios/users/register/` | No | Registrar usuario (devuelve token) |
| POST | `/api/usuarios/users/login/` | No | Iniciar sesión (devuelve token) |
| POST | `/api/usuarios/users/logout/` | Sí | Cerrar sesión (invalida token) |

### 📚 Libros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/libros/libros/` | Listar / crear libros |
| GET/PUT/DELETE | `/api/libros/libros/{id}/` | Gestionar libro específico |
| POST | `/api/libros/libros/{id}/prestar/` | Pedir libro prestado |
| GET/POST | `/api/libros/autores/` | Gestionar autores |
| GET/POST | `/api/libros/generos/` | Gestionar géneros |

### 🔄 Préstamos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/libros/prestamos/` | Ver / crear préstamos |
| POST | `/api/libros/prestamos/{id}/devolver/` | Devolver libro |

### 📊 Auditoría

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/auditoria/logs/` | Ver logs de auditoría |
| GET | `/api/auditoria/logs/export_excel/` | Exportar logs a Excel |
| GET | `/api/auditoria/logs/statistics/` | Estadísticas de uso |

Ejemplo de respuesta de estadísticas:

```json
{
  "total_logs": 150,
  "recent_logs": 45,
  "actions_by_type": {
    "Creación": 20,
    "Actualización": 15,
    "Préstamo": 8
  }
}
```

## 🎯 Roles de Usuario

| Rol | Límite Préstamos | Permisos |
|-----|-----------------|----------|
| Gratuito | 3 | Ver/crear préstamos propios |
| Premium | 10 | Ver/crear préstamos propios |
| Bibliotecario | 50 | Ver todos los préstamos + gestión completa |
| DBA | 100 | Acceso completo + auditoría |

## 🧪 Testing

Las pruebas usan SQLite automáticamente (sin necesidad de tener MariaDB corriendo).

```bash
# Ejecutar todas las pruebas
pytest

# Con reporte de cobertura
pytest --cov=libros --cov=usuarios --cov=auditoria --cov-report=html

# Pruebas específicas
pytest tests/test_integracion.py -v
```

Variables de entorno mínimas para correr tests localmente:

```bash
export SECRET_KEY=test-key
export USE_SQLITE=True
pytest
```

## 🏗️ Estructura del proyecto

```
libreria-api-django/
├── .github/workflows/      # CI con GitHub Actions
├── libreria_api/           # Configuración principal Django
│   └── settings.py
├── libros/                 # App de gestión de libros
├── usuarios/               # App de gestión de usuarios y roles
├── auditoria/              # App de auditoría y logs
├── tests/                  # Pruebas de integración
├── logs/                   # Logs de la aplicación (generado automáticamente)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## 📄 Licencia

Este proyecto está bajo licencia GPL-3.0 — ver archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Sebastian González Cacho** — [@SebastianGonzalezCacho](https://github.com/SebastianGonzalezCacho)
