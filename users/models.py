from django.db import models


class ClientM(models.Model):
    STATUS_CHOICES = [
        ('active', 'active'),
        ('inactive', 'inactive'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    admin_name = models.CharField(max_length=255)
    admin_email = models.EmailField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ClientUserM(models.Model):
    CLIENT_ADMIN = 'client_admin'
    CLIENT_USER = 'client_user'

    ROLE_CHOICES = [
        (CLIENT_ADMIN, 'client_admin'),
        (CLIENT_USER, 'client_user'),
    ]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    client = models.ForeignKey(ClientM, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_root_client_admin = models.BooleanField(default=False)
