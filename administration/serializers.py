from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from users.models import ClientM, ClientUserM


class UserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
        read_only_fields = fields


# class ClientUserReadSerializer(serializers.ModelSerializer):
#     user = UserReadSerializer(read_only=True)

#     class Meta:
#         model = ClientUserM
#         fields = ['id', 'name', 'email', 'role', 'status', 'created_at', 'updated_at', 'is_root_client_admin', 'user']
#         read_only_fields = fields


class ClientReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientM
        fields = ['id', 'name', 'admin_name', 'admin_email', 'status', 'created_at', 'updated_at', 'users']
        read_only_fields = fields


class ClientRootAdminSerialzier(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    client_root_admin_username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ClientM
        fields = ['id', 'name', 'admin_name', 'admin_email', 'created_at', 'updated_at', 
                  'password', 'client_root_admin_username']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        client_root_admin_username = validated_data.pop('client_root_admin_username', None)
        with transaction.atomic():
            user = User.objects.create_user(username=client_root_admin_username)
            user.set_password(password)
            user.save()
            client = ClientM.objects.create(**validated_data)
            ClientUserM.objects.create(user=user, client=client,
                                       role=ClientUserM.CLIENT_ADMIN,
                                       is_root_client_admin=True)
        return client
    

class ClientUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    user_read = UserReadSerializer(source='user', read_only=True)

    class Meta:
        model = ClientUserM
        fields = ['id', 'role', 'client', 'created_at', 'updated_at', 'user', 'user_read',
                  'username', 'password']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        username = validated_data.pop('username')

        with transaction.atomic():
            user = User.objects.create_user(username=username)
            user.set_password(password)
            user.save()
            client_user = ClientUserM.objects.create(user=user, **validated_data)
        return client_user
