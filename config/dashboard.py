from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from taches.models import Task, Project, Notification
from utilisateurs.models import User

def dashboard_callback(request, context):
    """
    Callback pour personnaliser le dashboard selon l'utilisateur
    """
    user = request.user
    
    # Statistiques communes
    context.update({
        'notifications_non_lues': Notification.objects.filter(user=user, is_read=False).count(),
        'date_aujourdhui': timezone.now().strftime("%d %B %Y"),
    })
    
    # Statistiques selon le rôle
    if user.role == 'directeur':
        context.update({
            'total_projets': Project.objects.count(),
            'total_utilisateurs': User.objects.count(),
            'projets_actifs': Project.objects.filter(status='active').count(),
            'taches_en_cours': Task.objects.filter(status='in_progress').count(),
            'taches_retard': Task.objects.filter(is_completed=False, due_date__lt=timezone.now()).count(),
        })
    elif user.role == 'coordinateur' and user.department:
        context.update({
            'projets_departement': Project.objects.filter(department=user.department).count(),
            'membres_departement': User.objects.filter(department=user.department).count(),
            'taches_departement': Task.objects.filter(project__department=user.department).count(),
        })
    elif user.role == 'responsable_section' and user.section:
        context.update({
            'membres_section': User.objects.filter(section=user.section).count(),
            'taches_section': Task.objects.filter(assigned_to__section=user.section).distinct().count(),
        })
    
    # Statistiques personnelles
    context.update({
        'mes_taches': Task.objects.filter(assigned_to=user).count(),
        'mes_taches_terminees': Task.objects.filter(assigned_to=user, is_completed=True).count(),
        'mes_taches_retard': Task.objects.filter(assigned_to=user, is_completed=False, due_date__lt=timezone.now()).count(),
        'prochaines_echeances': Task.objects.filter(assigned_to=user, is_completed=False).order_by('due_date')[:5],
    })
    
    return context