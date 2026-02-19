from django.utils import timezone

class ActivityLoggerMixin:
    """Mixin pour logger les activités utilisateur"""
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self.log_activity(instance, 'created')
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self.log_activity(instance, 'updated')
    
    def log_activity(self, instance, action):
        from utilisateurs.models import UserActivity
        UserActivity.objects.create(
            user=self.request.user,
            action=f"{action}_{instance.__class__.__name__.lower()}",
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip