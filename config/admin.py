from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.urls import reverse

class LogEntryAdmin(UnfoldModelAdmin):
    """Administration des logs d'activité Django"""
    list_display = ['action_time', 'user_link', 'content_type', 'object_repr', 'action_flag_display', 'change_message']
    list_filter = ['action_flag', 'content_type', 'action_time']
    search_fields = ['object_repr', 'change_message', 'user__email']
    readonly_fields = ['action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message']
    
    @display(description="Utilisateur")
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:utilisateurs_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
        return '-'
    
    @display(description="Action", label=True)
    def action_flag_display(self, obj):
        colors = {1: 'green', 2: 'orange', 3: 'red'}
        labels = {1: 'Ajout', 2: 'Modification', 3: 'Suppression'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.action_flag, 'gray'),
            labels.get(obj.action_flag, '')
        )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Enregistrer LogEntry si ce n'est pas déjà fait
if not admin.site.is_registered(LogEntry):
    admin.site.register(LogEntry, LogEntryAdmin)

# Personnalisation du site admin
admin.site.site_header = "Gestion de Projet"
admin.site.site_title = "Gestion de Projet"
admin.site.index_title = "Tableau de Bord"
admin.empty_value_display = '-'