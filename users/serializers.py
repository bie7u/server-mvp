from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from users.models import ClientUserM


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Find user by email
            try:
                user = User.objects.get(email=email)
                # Authenticate using username and password
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                user = None

            if not user:
                raise serializers.ValidationError('Invalid credentials')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')

            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role information.
    """
    role = serializers.SerializerMethodField()
    clientId = serializers.SerializerMethodField()
    clientName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'clientId', 'clientName']
        read_only_fields = ['id', 'username', 'email']

    def _get_client_user(self, obj):
        """
        Cache ClientUserM lookup to avoid N+1 queries.
        """
        if not hasattr(obj, '_cached_client_user'):
            try:
                obj._cached_client_user = ClientUserM.objects.select_related('client').get(user=obj)
            except ClientUserM.DoesNotExist:
                obj._cached_client_user = None
        return obj._cached_client_user

    def get_role(self, obj):
        """
        Get user role from ClientUserM or determine if root_admin.
        """
        client_user = self._get_client_user(obj)
        if client_user:
            if client_user.is_root_client_admin:
                return 'root_admin'
            return client_user.role
        # If user is superuser/staff but not in ClientUserM, treat as root_admin
        if obj.is_superuser or obj.is_staff:
            return 'root_admin'
        return None

    def get_clientId(self, obj):
        """
        Get client ID if user is associated with a client.
        """
        client_user = self._get_client_user(obj)
        if client_user and client_user.client:
            return client_user.client.id
        return None

    def get_clientName(self, obj):
        """
        Get client name if user is associated with a client.
        """
        client_user = self._get_client_user(obj)
        if client_user and client_user.client:
            return client_user.client.name
        return None
