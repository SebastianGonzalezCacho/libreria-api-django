from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PerfilUsuarioViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfiles', PerfilUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]