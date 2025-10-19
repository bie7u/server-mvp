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

    def get_role(self, obj):
        """
        Get user role from ClientUserM or determine if root_admin.
        """
        try:
            client_user = ClientUserM.objects.get(user=obj)
            if client_user.is_root_client_admin:
                return 'root_admin'
            return client_user.role
        except ClientUserM.DoesNotExist:
            # If user is superuser/staff but not in ClientUserM, treat as root_admin
            if obj.is_superuser or obj.is_staff:
                return 'root_admin'
            return None

    def get_clientId(self, obj):
        """
        Get client ID if user is associated with a client.
        """
        try:
            client_user = ClientUserM.objects.get(user=obj)
            return client_user.client.id if client_user.client else None
        except ClientUserM.DoesNotExist:
            return None

    def get_clientName(self, obj):
        """
        Get client name if user is associated with a client.
        """
        try:
            client_user = ClientUserM.objects.get(user=obj)
            return client_user.client.name if client_user.client else None
        except ClientUserM.DoesNotExist:
            return None
