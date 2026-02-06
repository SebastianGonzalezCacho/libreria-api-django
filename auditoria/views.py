from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AuditLog
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import logging

audit_logger = logging.getLogger('audit')

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.perfil.tipo_usuario in ['bibliotecario', 'dba']:
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Exportar logs de auditoría a Excel"""
        queryset = self.get_queryset()
        
        # Crear libro Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Logs de Auditoría"
        
        # Encabezados
        headers = ['Fecha', 'Usuario', 'Acción', 'Tipo Objeto', 'ID Objeto', 'Objeto', 'Cambios', 'IP']
        ws.append(headers)
        
        # Estilos para encabezados
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_alignment = Alignment(horizontal='center')
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Datos
        for log in queryset:
            row = [
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.username if log.user else 'N/A',
                log.get_action_display(),
                log.object_type,
                log.object_id or '',
                log.object_repr,
                str(log.changes),
                log.ip_address or ''
            ]
            ws.append(row)
        
        # Autoajustar columnas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Guardar en memoria
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        wb.save(response)
        
        # Log de exportación
        audit_logger.info(
            f'export_excel',
            extra={
                'user': request.user.username,
                'action': 'EXPORT',
                'object_type': 'AuditLog',
                'changes': {'exported_records': queryset.count()}
            }
        )
        
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de auditoría"""
        queryset = self.get_queryset()
        
        # Últimos 30 días
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = queryset.filter(timestamp__gte=thirty_days_ago)
        
        stats = {
            'total_logs': queryset.count(),
            'recent_logs': recent_logs.count(),
            'actions_by_type': {},
            'objects_by_type': {},
            'top_users': {}
        }
        
        # Estadísticas por acción
        for log in recent_logs:
            action = log.get_action_display()
            stats['actions_by_type'][action] = stats['actions_by_type'].get(action, 0) + 1
        
        # Estadísticas por tipo de objeto
        for log in recent_logs:
            obj_type = log.object_type
            stats['objects_by_type'][obj_type] = stats['objects_by_type'].get(obj_type, 0) + 1
        
        # Usuarios más activos
        for log in recent_logs:
            if log.user:
                username = log.user.username
                stats['top_users'][username] = stats['top_users'].get(username, 0) + 1
        
        return Response(stats)

class LoginLogoutAPIView(APIView):
    """API para registrar inicios y cierres de sesión"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        action = request.data.get('action')  # 'login' o 'logout'
        user = request.user if request.user.is_authenticated else None
        
        if action == 'login' and user:
            AuditLog.objects.create(
                user=user,
                action='LOGIN',
                object_type='User',
                object_id=user.pk,
                object_repr=str(user),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                changes={'login_success': True}
            )
        elif action == 'logout' and user:
            AuditLog.objects.create(
                user=user,
                action='LOGOUT',
                object_type='User',
                object_id=user.pk,
                object_repr=str(user),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                changes={'logout_success': True}
            )
        
        return Response({'status': 'success'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip