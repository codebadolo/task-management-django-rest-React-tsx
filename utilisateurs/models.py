from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField

class CustomUserManager(BaseUserManager):
    """Gestionnaire personnalisé pour l'authentification par email"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur standard"""
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un superutilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'directeur')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class Poste(models.Model):
    """Modèle pour les postes (gestion dynamique)"""
    CATEGORIE_CHOICES = (
        ('direction', 'Direction'),
        ('management', 'Management'),
        ('technique', 'Technique'),
        ('support', 'Support'),
        ('commercial', 'Commercial'),
        ('administratif', 'Administratif'),
        ('autre', 'Autre'),
    )
    
    titre = models.CharField(max_length=100, unique=True, verbose_name="Titre du poste")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='autre', verbose_name="Catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    niveau_hierarchique = models.IntegerField(default=1, verbose_name="Niveau hiérarchique", 
                                              help_text="1 = plus bas, 10 = plus haut")
    
    # Visibilité
    est_actif = models.BooleanField(default=True, verbose_name="Poste actif")
    peut_gerer_equipe = models.BooleanField(default=False, verbose_name="Peut gérer une équipe")
    peut_creer_projets = models.BooleanField(default=False, verbose_name="Peut créer des projets")
    peut_valider_taches = models.BooleanField(default=False, verbose_name="Peut valider des tâches")
    
    # Apparence
    color = ColorField(default='#3498db', verbose_name="Couleur")
    icon = models.CharField(max_length=50, default='fa-solid fa-briefcase', verbose_name="Icône FontAwesome")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Poste"
        verbose_name_plural = "Postes"
        ordering = ['-niveau_hierarchique', 'titre']
    
    def __str__(self):
        return f"{self.titre} (Niv. {self.niveau_hierarchique})"
    
    def get_icon_html(self):
        return f'<i class="{self.icon}" style="color: {self.color};"></i>'


class Department(models.Model):
    """Modèle pour les départements"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    color = ColorField(default='#3498db', verbose_name="Couleur")
    icon = models.CharField(max_length=50, default='fa-solid fa-building', verbose_name="Icône FontAwesome")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['name']

    def __str__(self):
        return self.name


class Section(models.Model):
    """Modèle pour les sections"""
    # AJOUTER CE CHAMP
    responsable = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sections_responsables',
        verbose_name="Responsable"
    )
    name = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=10, verbose_name="Code")
    
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='sections',
        verbose_name="Département"
    )
    
    description = models.TextField(blank=True, verbose_name="Description")
    color = ColorField(default='#2ecc71', verbose_name="Couleur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        unique_together = ['code', 'department']
        ordering = ['department__name', 'name']

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Competence(models.Model):
    """Modèle pour les compétences"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    categorie = models.CharField(max_length=50, blank=True, verbose_name="Catégorie")
    
    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['categorie', 'nom']
    
    def __str__(self):
        return self.nom


class User(AbstractUser):
    """Modèle utilisateur personnalisé avec authentification par email"""
    
    ROLE_CHOICES = (
        ('directeur', '🏢 Directeur'),
        ('coordinateur', '📊 Coordinateur'),
        ('responsable_section', '👥 Responsable de Section'),
        ('membre', '👤 Membre'),
    )
    
    # Remplacer username par email pour l'authentification
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False,
        help_text='Optionnel. Ne pas utiliser pour l\'authentification.'
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    
    # Informations personnelles
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    profile_photo = models.ImageField(
        upload_to='profiles/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )
    
    # Informations professionnelles
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='membre',
        verbose_name="Rôle système"
    )
    poste = models.ForeignKey(
        Poste,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Poste"
    )
    
    # Relations - Utiliser des chaînes pour éviter les imports circulaires
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Département"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Section"
    )
    
    # Compétences
    competences = models.ManyToManyField(
        Competence,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Compétences"
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    phone_pro = models.CharField(max_length=20, blank=True, verbose_name="Téléphone professionnel")
    
    # Informations supplémentaires
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    code_postal = models.CharField(max_length=10, blank=True, verbose_name="Code postal")
    pays = models.CharField(max_length=100, default='France', verbose_name="Pays")
    
    # Dates importantes
    date_embauche = models.DateField(default=timezone.now, verbose_name="Date d'embauche")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    last_active = models.DateTimeField(null=True, blank=True, verbose_name="Dernière activité")
    
    # Préférences
    notification_email = models.BooleanField(default=True, verbose_name="Notifications par email")
    notification_desktop = models.BooleanField(default=True, verbose_name="Notifications bureau")
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Clair'), ('dark', 'Sombre'), ('auto', 'Automatique')],
        default='auto',
        verbose_name="Préférence de thème"
    )
    langue = models.CharField(
        max_length=10,
        choices=[('fr', 'Français'), ('en', 'Anglais')],
        default='fr',
        verbose_name="Langue"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs_crees',
        verbose_name="Créé par"
    )
    
    # Utiliser le gestionnaire personnalisé
    objects = CustomUserManager()
    
    # Définir email comme champ d'authentification principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['department', 'section']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"
    
    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Retourne le prénom"""
        return self.first_name
    
    def get_initials(self):
        """Retourne les initiales pour l'avatar"""
        first = self.first_name[0] if self.first_name else ''
        last = self.last_name[0] if self.last_name else ''
        return (first + last).upper() or self.email[0].upper()
    
    def get_avatar_url(self):
        """Retourne l'URL de l'avatar ou None"""
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return None
    
    def can_manage_team(self):
        """Vérifie si l'utilisateur peut gérer une équipe"""
        if self.poste:
            return self.poste.peut_gerer_equipe
        return self.role in ['directeur', 'coordinateur', 'responsable_section']
    
    def can_create_projects(self):
        """Vérifie si l'utilisateur peut créer des projets"""
        if self.poste:
            return self.poste.peut_creer_projets
        return self.role in ['directeur', 'coordinateur']
    
    def can_validate_tasks(self):
        """Vérifie si l'utilisateur peut valider des tâches"""
        if self.poste:
            return self.poste.peut_valider_taches
        return self.role in ['directeur', 'coordinateur', 'responsable_section']
    
    def get_team_members(self):
        """Retourne les membres de l'équipe selon le rôle"""
        if self.role == 'directeur':
            from .models import User  # Import local pour éviter les cycles
            return User.objects.all()
        elif self.role == 'coordinateur' and self.department:
            from .models import User
            return User.objects.filter(department=self.department)
        elif self.role == 'responsable_section' and self.section:
            from .models import User
            return User.objects.filter(section=self.section)
        return User.objects.none()
    
    def save(self, *args, **kwargs):
        # S'assurer que le username est défini (pour compatibilité Django)
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """Suivi de l'activité des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255, verbose_name="Action")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateurs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"