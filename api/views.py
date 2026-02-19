from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from .serializers import LoginSerializer, TokenResponseSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from utilisateurs.models import User, UserActivity
from taches.models import Project, Task, Notification
from utilisateurs.serializers import UserActivitySerializer
from taches.serializers import TaskListSerializer, NotificationSerializer
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            
            data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data
            }
            
            return Response({
                'status': 'success',
                'data': data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logout(request)
            
            return Response({
                'status': 'success',
                'message': 'Déconnexion réussie'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'status': 'error',
                'message': 'Refresh token requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            return Response({
                'status': 'success',
                'data': {
                    'access': str(token.access_token)
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Token invalide'
            }, status=status.HTTP_401_UNAUTHORIZED)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    



class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Statistiques de base
        stats = {
            'projects': {
                'total': Project.objects.count(),
                'active': Project.objects.filter(status='active').count(),
                'completed': Project.objects.filter(status='completed').count(),
            },
            'tasks': {
                'total': Task.objects.count(),
                'todo': Task.objects.filter(status='todo').count(),
                'in_progress': Task.objects.filter(status='in_progress').count(),
                'completed': Task.objects.filter(is_completed=True).count(),
                'overdue': Task.objects.filter(due_date__lt=today, is_completed=False).count(),
            },
            'users': {
                'total': User.objects.count(),
                'active_today': User.objects.filter(last_active__date=today).count(),
            },
            'notifications': {
                'unread': Notification.objects.filter(user=user, is_read=False).count(),
            }
        }
        
        # Statistiques personnalisées selon le rôle
        if user.role in ['directeur', 'coordinateur']:
            stats['team_performance'] = self.get_team_performance(user)
        
        if user.role == 'directeur':
            stats['department_stats'] = self.get_department_stats()
        
        return Response({'status': 'success', 'data': stats})
    
    def get_team_performance(self, user):
        team = user.get_team_members()
        tasks = Task.objects.filter(assigned_to__in=team)
        
        return {
            'team_tasks': tasks.count(),
            'team_completed': tasks.filter(is_completed=True).count(),
            'team_overdue': tasks.filter(due_date__lt=timezone.now(), is_completed=False).count(),
        }
    
    def get_department_stats(self):
        from utilisateurs.models import Department
        return Department.objects.annotate(
            user_count=Count('utilisateurs'),
            project_count=Count('projects')
        ).values('name', 'user_count', 'project_count', 'color')

class DashboardActivitiesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        limit = int(request.query_params.get('limit', 10))
        
        activities = []
        
        # Activités des tâches récentes
        if user.role == 'directeur':
            tasks = Task.objects.filter(is_completed=True).order_by('-completed_date')[:limit]
        elif user.role == 'coordinateur' and user.department:
            tasks = Task.objects.filter(
                project__department=user.department,
                is_completed=True
            ).order_by('-completed_date')[:limit]
        else:
            tasks = Task.objects.filter(assigned_to=user, is_completed=True).order_by('-completed_date')[:limit]
        
        for task in tasks:
            activities.append({
                'type': 'task_completed',
                'title': f'Tâche terminée: {task.title}',
                'project': task.project.name,
                'user': task.assigned_to.first().get_full_name() if task.assigned_to.exists() else None,
                'date': task.completed_date,
                'icon': 'fa-check-circle',
                'color': 'success'
            })
        
        # Projets récents
        projects = Project.objects.order_by('-created_at')[:limit]
        for project in projects:
            activities.append({
                'type': 'project_created',
                'title': f'Nouveau projet: {project.name}',
                'department': project.department.name,
                'user': project.created_by.get_full_name() if project.created_by else None,
                'date': project.created_at,
                'icon': 'fa-folder-open',
                'color': 'info'
            })
        
        # Notifications non lues
        notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:limit]
        for notif in notifications:
            activities.append({
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'date': notif.created_at,
                'icon': 'fa-bell',
                'color': 'warning'
            })
        
        # Trier par date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return Response({
            'status': 'success',
            'data': activities[:limit]
        })

class DashboardChartDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now()
        last_30_days = [today - timedelta(days=x) for x in range(29, -1, -1)]
        
        # Évolution des tâches
        tasks_timeline = []
        for day in last_30_days:
            tasks = Task.objects.filter(
                created_at__date=day.date()
            ).aggregate(
                created=Count('id'),
                completed=Count('id', filter=Q(completed_date__date=day.date()))
            )
            tasks_timeline.append({
                'date': day.strftime('%d/%m'),
                'created': tasks['created'],
                'completed': tasks['completed']
            })
        
        # Répartition par statut
        tasks_by_status = Task.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Tâches par projet (top 5)
        tasks_by_project = Project.objects.annotate(
            task_count=Count('tasks')
        ).order_by('-task_count')[:5].values('name', 'task_count')
        
        return Response({
            'status': 'success',
            'data': {
                'tasks_timeline': tasks_timeline,
                'tasks_by_status': list(tasks_by_status),
                'tasks_by_project': list(tasks_by_project),
            }
        })   
