from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from utilisateurs.models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Compte désactivé')
                update_last_login(None, user)
                return user
            else:
                raise serializers.ValidationError('Email ou mot de passe incorrect')
        else:
            raise serializers.ValidationError('Email et mot de passe requis')

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'initials', 'avatar_url', 'role', 'poste', 'department',
            'section', 'phone', 'ville', 'theme_preference', 'langue',
            'notification_email', 'notification_desktop', 'permissions',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_initials(self, obj):
        return obj.get_initials()
    
    def get_avatar_url(self, obj):
        return obj.get_avatar_url()
    
    def get_permissions(self, obj):
        return {
            'can_manage_team': obj.can_manage_team(),
            'can_create_projects': obj.can_create_projects(),
            'can_validate_tasks': obj.can_validate_tasks(),
        }

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()