from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Sum, Avg
from django.db.models.functions import TruncDate, TruncMonth
from .models import Project, Task, Notification
from utilisateurs.models import User

class DashboardMetrics:
    """Classe pour calculer les métriques du dashboard"""
    
    @staticmethod
    def get_stats():
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'projects': {
                'total': Project.objects.count(),
                'active': Project.objects.filter(status='active').count(),
                'completed': Project.objects.filter(status='completed').count(),
                'on_hold': Project.objects.filter(status='on_hold').count(),
                'new_this_week': Project.objects.filter(created_at__date__gte=week_ago).count(),
            },
            'tasks': {
                'total': Task.objects.count(),
                'todo': Task.objects.filter(status='todo').count(),
                'in_progress': Task.objects.filter(status='in_progress').count(),
                'review': Task.objects.filter(status='review').count(),
                'completed': Task.objects.filter(is_completed=True).count(),
                'overdue': Task.objects.filter(
                    due_date__date__lt=today,
                    is_completed=False
                ).count(),
                'due_today': Task.objects.filter(
                    due_date__date=today,
                    is_completed=False
                ).count(),
                'due_this_week': Task.objects.filter(
                    due_date__date__range=[today, today + timedelta(days=7)],
                    is_completed=False
                ).count(),
            },
            'users': {
                'total': User.objects.count(),
                'active_today': User.objects.filter(last_active__date=today).count(),
                'active_this_week': User.objects.filter(last_active__date__gte=week_ago).count(),
                'by_role': dict(
                    User.objects.values('role')
                    .annotate(count=Count('id'))
                    .values_list('role', 'count')
                ),
            },
            'notifications': {
                'total': Notification.objects.count(),
                'unread': Notification.objects.filter(is_read=False).count(),
            }
        }
    
    @staticmethod
    def get_activity_feed(limit=10):
        """Retourne les activités récentes"""
        activities = []
        
        # Tâches récemment complétées
        completed_tasks = Task.objects.filter(
            is_completed=True,
            completed_date__isnull=False
        ).select_related('project')[:limit]
        
        for task in completed_tasks:
            activities.append({
                'type': 'task_completed',
                'title': f'Tâche complétée: {task.title}',
                'project': task.project.name,
                'user': task.assigned_to.first() if task.assigned_to.exists() else None,
                'date': task.completed_date,
                'icon': 'fa-check-circle',
                'color': 'success'
            })
        
        # Nouveaux projets
        new_projects = Project.objects.order_by('-created_at')[:limit]
        for project in new_projects:
            activities.append({
                'type': 'project_created',
                'title': f'Nouveau projet: {project.name}',
                'department': project.department.name,
                'user': project.created_by,
                'date': project.created_at,
                'icon': 'fa-folder-open',
                'color': 'info'
            })
        
        # Notifications récentes
        recent_notifications = Notification.objects.filter(
            is_read=False
        ).order_by('-created_at')[:limit]
        
        for notif in recent_notifications:
            activities.append({
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'user': notif.user,
                'date': notif.created_at,
                'icon': 'fa-bell',
                'color': 'warning'
            })
        
        # Trier par date
        activities.sort(key=lambda x: x['date'], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def get_chart_data():
        """Données pour les graphiques"""
        today = timezone.now()
        last_30_days = [today - timedelta(days=x) for x in range(29, -1, -1)]
        
        # Progression des tâches par jour
        tasks_by_day = []
        for day in last_30_days:
            tasks = Task.objects.filter(
                created_at__date=day.date()
            ).aggregate(
                created=Count('id'),
                completed=Count('id', filter=Q(completed_date__date=day.date()))
            )
            tasks_by_day.append({
                'date': day.strftime('%d/%m'),
                'created': tasks['created'],
                'completed': tasks['completed']
            })
        
        # Répartition des tâches par statut
        tasks_by_status = Task.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Tâches par projet (top 5)
        tasks_by_project = Project.objects.annotate(
            task_count=Count('tasks')
        ).order_by('-task_count')[:5].values('name', 'task_count')
        
        return {
            'tasks_timeline': tasks_by_day,
            'tasks_by_status': list(tasks_by_status),
            'tasks_by_project': list(tasks_by_project),
            'project_progress': DashboardMetrics.get_project_progress(),
        }
    
    @staticmethod
    def get_project_progress():
        """Progression des projets actifs"""
        active_projects = Project.objects.filter(status='active')[:5]
        progress_data = []
        
        for project in active_projects:
            total_tasks = project.tasks.count()
            completed_tasks = project.tasks.filter(is_completed=True).count()
            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            progress_data.append({
                'name': project.name,
                'code': project.code,
                'total_tasks': total_tasks,
                'completed': completed_tasks,
                'progress': round(progress, 1),
                'end_date': project.end_date,
                'priority': project.get_priority_display(),
            })
        
        return progress_data