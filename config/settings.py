"""
Django settings for project_management project.
"""

from pathlib import Path
import os
from decouple import config
from django.urls import reverse_lazy
from django.conf.urls.static import static
from django.contrib.messages import constants as messages
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    #'admin_volt.apps.AdminVoltConfig',
    
    # Django Admin Interface (pour personnaliser l'apparence)
    #'admin_interface',
    'jazzmin',
    'colorfield',
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
      "corsheaders",
    # Applications tierces
    'drf_yasg',
    'rangefilter',
    'import_export',
    'crispy_forms',
    'crispy_bootstrap4',
    'rest_framework',
    'channels',
      'chartjs',  # Pour les graphiques
    
    # Applications locales
    'utilisateurs',
    'taches',
]

MIDDLEWARE = [
        "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'templates/admin',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user model
AUTH_USER_MODEL = 'utilisateurs.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Login URLs
LOGIN_URL = 'admin:login'
LOGIN_REDIRECT_URL = 'admin:index'
LOGOUT_REDIRECT_URL = 'admin:login'

# Email configuration (pour les notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Pour le développement
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Pour la production
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Configuration Unfold
'''
'''
from django.urls import reverse_lazy
from django.utils import timezone
from django.templatetags.static import static
import os

from django.urls import reverse_lazy
from django.utils import timezone
from django.templatetags.static import static
import os

# Channel layers (for real-time notifications)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Pour le développement
        # Pour la production avec Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('redis', 6379)],
        # },
    },
}

# REST Framework
# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    #'EXCEPTION_HANDLER': 'api.utils.custom_exception_handler',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS (si nécessaire)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# settings.py - Configuration Jazzmin

JAZZMIN_SETTINGS = {
    # Titres et branding
    "site_title": "Gestion de Projet",
    "site_header": "Gestion de Projet",
    "site_brand": "Gestion de Projet",
    "site_logo": "img/logo.png",  # Placez votre logo dans static/img/
    "site_logo_classes": "img-circle",
    "site_icon": "img/favicon.ico",
    "welcome_sign": "Bienvenue sur la plateforme de gestion de projet",
    "copyright": f"Gestion de Projet © {timezone.now().year}",
    
    # Avatar utilisateur
    "user_avatar": "profile_photo",  # Champ dans votre modèle User
    
    # Configuration de la recherche
    "search_model": [
        "utilisateurs.User", 
        "taches.Project", 
        "taches.Task"
    ],
    
    # Liens du menu supérieur
    "topmenu_links": [
        # Accueil
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
        
        # Tableau de bord
        {"name": "Dashboard", "url": "admin_dashboard", "new_window": False},
        
        # Documentation / Support
        {"name": "Support", "url": "https://github.com/your-repo/issues", "new_window": True},
    ],
    
    # Menu utilisateur (en haut à droite)
    "usermenu_links": [
        {"name": "Mon Profil", "url": "admin:utilisateurs_user_change", "args": [lambda request: request.user.id]},
        {"model": "taches.notification", "badge": lambda request: request.user.notifications.filter(is_read=False).count()},
    ],
    
    # Configuration du menu latéral
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Ordre des applications et modèles
    "order_with_respect_to": [
        "utilisateurs", 
        "utilisateurs.User",
        "utilisateurs.Poste",
        "utilisateurs.Department",
        "utilisateurs.Section",
        "utilisateurs.Competence",
        "taches",
        "taches.Project",
        "taches.Task",
        "taches.Notification",
    ],
    
    # Liens personnalisés par rôle
    "custom_links": {
        "utilisateurs": [
            {
                "name": "Mon Équipe",
                "url": "custom_team_view",  # À créer
                "icon": "fas fa-users",
                "permissions": ["utilisateurs.view_user"],
                "condition": lambda request: request.user.can_manage_team(),
            },
            {
                "name": "Statistiques RH",
                "url": "custom_hr_stats",
                "icon": "fas fa-chart-bar",
                "permissions": ["utilisateurs.view_user"],
                "condition": lambda request: request.user.role in ['directeur', 'coordinateur'],
            },
        ],
        "taches": [
            {
                "name": "Mes Tâches",
                "url": "my_tasks_view",
                "icon": "fas fa-tasks",
                "permissions": ["taches.view_task"],
                "condition": lambda request: True,  # Visible par tous
            },
            {
                "name": "Tâches en Retard",
                "url": "overdue_tasks_view",
                "icon": "fas fa-exclamation-triangle",
                "permissions": ["taches.view_task"],
                "condition": lambda request: request.user.role in ['directeur', 'coordinateur', 'responsable_section'],
            },
            {
                "name": "Calendrier des Projets",
                "url": "project_calendar_view",
                "icon": "fas fa-calendar-alt",
                "permissions": ["taches.view_project"],
                "condition": lambda request: True,
            },
            {
                "name": "Rapports d'Avancement",
                "url": "progress_reports_view",
                "icon": "fas fa-chart-line",
                "permissions": ["taches.view_project"],
                "condition": lambda request: request.user.role in ['directeur', 'coordinateur'],
            },
        ],
    },
    
    # Icônes pour les applications et modèles
    "icons": {
        # Applications
        "utilisateurs": "fas fa-users-cog",
        "taches": "fas fa-tasks",
        "auth": "fas fa-lock",
        
        # Modèles utilisateurs
        "utilisateurs.User": "fas fa-user",
        "utilisateurs.Poste": "fas fa-briefcase",
        "utilisateurs.Department": "fas fa-building",
        "utilisateurs.Section": "fas fa-layer-group",
        "utilisateurs.Competence": "fas fa-code",
        "utilisateurs.UserActivity": "fas fa-history",
        
        # Modèles tâches
        "taches.Project": "fas fa-project-diagram",
        "taches.Task": "fas fa-check-circle",
        "taches.TaskComment": "fas fa-comment",
        "taches.TaskAttachment": "fas fa-paperclip",
        "taches.Notification": "fas fa-bell",
        
        # Modèles auth Django
        "auth.Group": "fas fa-users",
        "auth.Permission": "fas fa-key",
    },
    
    # Icônes par défaut
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    
    # Configuration des formulaires
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "utilisateurs.User": "collapsible",
        "taches.Project": "horizontal_tabs",
        "taches.Task": "vertical_tabs",
    },
    
    # Personnalisation UI
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_admin.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,  # Mettre à True pour le développement
    
    # Sélecteur de langue
  #  "language_chooser": True,
}

# Configuration supplémentaire
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}