from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, LoginLogoutAPIView

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', LoginLogoutAPIView.as_view(), name='auth-logging'),
]