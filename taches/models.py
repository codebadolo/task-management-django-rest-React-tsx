from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
# NE PAS importer directement les modèles
from utilisateurs.models import User, Department

class Project(models.Model):
    """Modèle pour les projets"""
    PRIORITY_CHOICES = (
        (1, 'Très basse'),
        (2, 'Basse'),
        (3, 'Moyenne'),
        (4, 'Haute'),
        (5, 'Critique'),
    )
    
    STATUS_CHOICES = (
        ('planning', 'Planification'),
        ('active', 'En cours'),
        ('on_hold', 'En pause'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    )
    
    name = models.CharField(max_length=200, verbose_name="Nom")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(verbose_name="Description")
    
    # Utiliser des chaînes pour les ForeignKey
    department = models.ForeignKey(
        'utilisateurs.Department',  # Chaîne au lieu de l'import direct
        on_delete=models.CASCADE, 
        related_name='projects',
        verbose_name="Département"
    )
    
    coordinators = models.ManyToManyField(
        'utilisateurs.User',  # Chaîne au lieu de l'import direct
        related_name='coordinated_projects', 
        verbose_name="Coordinateurs",
        blank=True
    )
    
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3, verbose_name="Priorité")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name="Statut")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    
    created_by = models.ForeignKey(
        'utilisateurs.User',  # Chaîne au lieu de l'import direct
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_projects',
        verbose_name="Créé par"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-priority', 'end_date']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_progress(self):
        """Calcule la progression du projet basée sur les tâches"""
        tasks = self.tasks.all()
        if not tasks:
            return 0
        completed = tasks.filter(is_completed=True).count()
        return int((completed / tasks.count()) * 100)


class Task(models.Model):
    """Modèle pour les tâches avec support Kanban"""
    PRIORITY_CHOICES = (
        (1, 'Très basse'),
        (2, 'Basse'),
        (3, 'Moyenne'),
        (4, 'Haute'),
        (5, 'Urgente'),
    )
    
    COMPLEXITY_CHOICES = (
        (1, 'Très simple'),
        (2, 'Simple'),
        (3, 'Moyen'),
        (4, 'Complexe'),
        (5, 'Très complexe'),
    )
    
    STATUS_CHOICES = (
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('review', 'En revue'),
        ('done', 'Terminé'),
        ('blocked', 'Bloqué'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name="Projet"
    )
    
    assigned_to = models.ManyToManyField(
        'utilisateurs.User',  # Chaîne au lieu de l'import direct
        related_name='assigned_tasks',
        verbose_name="Assigné à",
        blank=True
    )
    
    created_by = models.ForeignKey(
        'utilisateurs.User',  # Chaîne au lieu de l'import direct
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_tasks',
        verbose_name="Créé par"
    )
    
    # Kanban fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="Statut")
    kanban_order = models.IntegerField(default=0, verbose_name="Ordre Kanban")
    
    # Priority and complexity
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3, verbose_name="Priorité")
    complexity = models.IntegerField(choices=COMPLEXITY_CHOICES, default=3, verbose_name="Complexité")
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Date de début")
    due_date = models.DateTimeField(verbose_name="Date d'échéance")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    
    # Tracking
    is_completed = models.BooleanField(default=False, verbose_name="Terminée")
    completion_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage de complétion"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['kanban_order', '-priority', 'due_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_date:
            self.completed_date = timezone.now()
            self.completion_percentage = 100
        elif not self.is_completed:
            self.completed_date = None
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Vérifie si la tâche est en retard"""
        if self.is_completed:
            return False
        return timezone.now() > self.due_date
    
    def get_time_remaining(self):
        """Retourne le temps restant en jours"""
        if self.is_completed:
            return 0
        delta = self.due_date - timezone.now()
        return max(0, delta.days)


class TaskComment(models.Model):
    """Commentaires sur les tâches"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name="Tâche")
    user = models.ForeignKey('utilisateurs.User', on_delete=models.CASCADE, verbose_name="Utilisateur")
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.user_id} sur {self.task.title}"


class TaskAttachment(models.Model):
    """Pièces jointes pour les tâches"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments', verbose_name="Tâche")
    user = models.ForeignKey('utilisateurs.User', on_delete=models.CASCADE, verbose_name="Utilisateur")
    file = models.FileField(upload_to='task_attachments/%Y/%m/', verbose_name="Fichier")
    filename = models.CharField(max_length=255, verbose_name="Nom du fichier")
    file_size = models.IntegerField(default=0, verbose_name="Taille (octets)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    
    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        self.filename = self.file.name
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.filename


class Notification(models.Model):
    """Notifications pour les utilisateurs"""
    NOTIFICATION_TYPES = (
        ('task_assigned', 'Tâche assignée'),
        ('task_updated', 'Tâche mise à jour'),
        ('task_completed', 'Tâche terminée'),
        ('comment_added', 'Commentaire ajouté'),
        ('deadline_approaching', 'Échéance proche'),
        ('deadline_passed', 'Échéance dépassée'),
        ('project_created', 'Nouveau projet'),
        ('project_updated', 'Projet mis à jour'),
    )
    
    user = models.ForeignKey('utilisateurs.User', on_delete=models.CASCADE, related_name='notifications', verbose_name="Utilisateur")
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name="Type")
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tâche liée")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Projet lié")
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return self.title
    
    def mark_as_read(self):
        self.is_read = True
        self.save()