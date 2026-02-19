from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .admin_dashboard import DashboardMetrics

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer toutes les métriques
        context['stats'] = DashboardMetrics.get_stats()
        context['activities'] = DashboardMetrics.get_activity_feed()
        context['chart_data'] = DashboardMetrics.get_chart_data()
        context['project_progress'] = DashboardMetrics.get_project_progress()
        
        return context
    

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Project, Task, TaskComment, TaskAttachment, Notification
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    TaskListSerializer, TaskDetailSerializer, TaskCreateUpdateSerializer,
    TaskStatusUpdateSerializer, TaskCommentSerializer, TaskAttachmentSerializer,
    NotificationSerializer
)
from api.permissions import (
    IsDirector, IsCoordinator, IsDepartmentHead,
    IsSectionHead, CanCreateProject, CanValidateTask
)
from core.pagination import StandardResultsSetPagination
from core.mixins import ActivityLoggerMixin

class ProjectViewSet(viewsets.ModelViewSet, ActivityLoggerMixin):
    queryset = Project.objects.all().select_related('department', 'created_by')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'department']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['-priority', 'end_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        elif self.action in ['create']:
            permission_classes = [CanCreateProject]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsDirector|IsCoordinator]
        else:
            permission_classes = [IsDirector]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'directeur':
            return queryset
        elif user.role == 'coordinateur':
            if user.department:
                return queryset.filter(
                    Q(department=user.department) | 
                    Q(coordinators=user)
                ).distinct()
            return queryset.filter(coordinators=user)
        elif user.role == 'responsable_section' and user.section:
            return queryset.filter(
                Q(department=user.department) |
                Q(tasks__assigned_to=user)
            ).distinct()
        elif user.role == 'membre':
            return queryset.filter(tasks__assigned_to=user).distinct()
        
        return queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des projets"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        data = {
            'total': queryset.count(),
            'by_status': queryset.values('status').annotate(count=Count('id')),
            'by_priority': queryset.values('priority').annotate(count=Count('id')),
            'active': queryset.filter(status='active').count(),
            'completed': queryset.filter(status='completed').count(),
            'upcoming_deadlines': ProjectListSerializer(
                queryset.filter(
                    end_date__gte=today,
                    end_date__lte=today + timedelta(days=7)
                ).order_by('end_date')[:5], many=True
            ).data,
        }
        return Response({'status': 'success', 'data': data})
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Tâches d'un projet"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        # Filtrer selon les permissions
        if request.user.role == 'membre':
            tasks = tasks.filter(assigned_to=request.user)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response({'status': 'success', 'data': serializer.data})
    
    @action(detail=True, methods=['get'])
    def kanban(self, request, pk=None):
        """Vue Kanban du projet"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        if request.user.role == 'membre':
            tasks = tasks.filter(assigned_to=request.user)
        
        kanban_data = {
            'todo': TaskListSerializer(tasks.filter(status='todo'), many=True).data,
            'in_progress': TaskListSerializer(tasks.filter(status='in_progress'), many=True).data,
            'review': TaskListSerializer(tasks.filter(status='review'), many=True).data,
            'done': TaskListSerializer(tasks.filter(is_completed=True), many=True).data,
            'blocked': TaskListSerializer(tasks.filter(status='blocked'), many=True).data,
        }
        
        return Response({'status': 'success', 'data': kanban_data})
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Timeline du projet"""
        project = self.get_object()
        tasks = project.tasks.all().order_by('due_date')
        
        timeline_data = []
        for task in tasks:
            timeline_data.append({
                'id': task.id,
                'title': task.title,
                'start': task.start_date,
                'end': task.due_date,
                'status': task.status,
                'assigned_to': [f"{u.first_name} {u.last_name}" for u in task.assigned_to.all()]
            })
        
        return Response({'status': 'success', 'data': timeline_data})

class TaskViewSet(viewsets.ModelViewSet, ActivityLoggerMixin):
    queryset = Task.objects.all().select_related('project', 'created_by')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'complexity', 'is_completed', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['-priority', 'due_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'directeur':
            return queryset
        elif user.role == 'coordinateur':
            if user.department:
                return queryset.filter(
                    Q(project__department=user.department) |
                    Q(assigned_to=user)
                ).distinct()
            return queryset.filter(assigned_to=user)
        elif user.role == 'responsable_section' and user.section:
            return queryset.filter(
                Q(assigned_to__section=user.section) |
                Q(assigned_to=user)
            ).distinct()
        elif user.role == 'membre':
            return queryset.filter(assigned_to=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        
        # Créer des notifications pour les assignés
        from .models import Notification
        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                notification_type='task_assigned',
                title=f'Nouvelle tâche: {task.title}',
                message=f'Vous avez été assigné à la tâche "{task.title}" dans le projet {task.project.name}',
                task=task,
                project=task.project
            )
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Mes tâches assignées"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        
        # Statistiques
        stats = {
            'total': tasks.count(),
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'completed': tasks.filter(is_completed=True).count(),
            'overdue': tasks.filter(due_date__lt=timezone.now(), is_completed=False).count(),
        }
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return Response({
                'status': 'success',
                'stats': stats,
                'results': serializer.data,
                'count': tasks.count()
            })
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response({'status': 'success', 'stats': stats, 'data': serializer.data})
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Tâches en retard"""
        tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            is_completed=False
        ).order_by('due_date')
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response({'status': 'success', 'data': serializer.data})
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Tâches à venir (7 prochains jours)"""
        today = timezone.now()
        next_week = today + timedelta(days=7)
        
        tasks = self.get_queryset().filter(
            due_date__range=[today, next_week],
            is_completed=False
        ).order_by('due_date')
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response({'status': 'success', 'data': serializer.data})
    
    @action(detail=True, methods=['put'])
    def status(self, request, pk=None):
        """Mettre à jour le statut d'une tâche"""
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            task.status = serializer.validated_data['status']
            if 'completion_percentage' in serializer.validated_data:
                task.completion_percentage = serializer.validated_data['completion_percentage']
            
            if task.status == 'done':
                task.is_completed = True
                task.completed_date = timezone.now()
                task.completion_percentage = 100
                
                # Notification pour les créateurs
                Notification.objects.create(
                    user=task.created_by,
                    notification_type='task_completed',
                    title=f'Tâche terminée: {task.title}',
                    message=f'La tâche "{task.title}" a été marquée comme terminée',
                    task=task,
                    project=task.project
                )
            
            task.save()
            
            return Response({
                'status': 'success',
                'data': TaskDetailSerializer(task).data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Réassigner une tâche"""
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response({
                'status': 'error',
                'message': 'Liste d\'utilisateurs requise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from utilisateurs.models import User
        users = User.objects.filter(id__in=user_ids)
        task.assigned_to.set(users)
        
        # Créer des notifications
        for user in users:
            Notification.objects.create(
                user=user,
                notification_type='task_assigned',
                title=f'Nouvelle assignation: {task.title}',
                message=f'Vous avez été assigné à la tâche "{task.title}"',
                task=task,
                project=task.project
            )
        
        return Response({
            'status': 'success',
            'data': TaskDetailSerializer(task).data
        })
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valider une tâche (pour les responsables)"""
        task = self.get_object()
        
        if not request.user.can_validate_tasks():
            return Response({
                'status': 'error',
                'message': 'Vous n\'avez pas la permission de valider des tâches'
            }, status=status.HTTP_403_FORBIDDEN)
        
        task.is_completed = True
        task.completed_date = timezone.now()
        task.completion_percentage = 100
        task.status = 'done'
        task.save()
        
        # Notification pour les assignés
        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                notification_type='task_completed',
                title='Tâche validée',
                message=f'Votre tâche "{task.title}" a été validée',
                task=task,
                project=task.project
            )
        
        return Response({
            'status': 'success',
            'data': TaskDetailSerializer(task).data
        })

class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all().select_related('user', 'task')
    serializer_class = TaskCommentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task']
    ordering_fields = ['-created_at']
    
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        
        # Notifier les autres personnes assignées
        task = comment.task
        for user in task.assigned_to.exclude(id=self.request.user.id):
            Notification.objects.create(
                user=user,
                notification_type='comment_added',
                title=f'Nouveau commentaire sur {task.title}',
                message=f'{self.request.user.get_full_name()} a commenté la tâche "{task.title}"',
                task=task,
                project=task.project
            )

class TaskAttachmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachment.objects.all().select_related('user', 'task')
    serializer_class = TaskAttachmentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'notification_type']
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'status': 'success', 'data': {'count': count}})    