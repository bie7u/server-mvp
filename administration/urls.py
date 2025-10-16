from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ClientRootAdminViewSet, ClientUserViewSet

router = DefaultRouter()
router.register(r'clients', ClientRootAdminViewSet)

client_router = NestedDefaultRouter(router, r'clients', lookup='client')
client_router.register(r'client-users', ClientUserViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('', include(client_router.urls)),
]
