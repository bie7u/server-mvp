from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser
from users.models import ClientM, ClientUserM
from administration.serializers import ClientRootAdminSerialzier, ClientUserSerializer


class NestedGenericViewSet(viewsets.GenericViewSet):

    def _get_parent_param(self, kwargs):
        for key, value in kwargs.items():
            if key.endswith('_pk'):
                field = key[:-3]
                return field, value
            
    def get_queryset(self):
        parent_field, parent_value = self._get_parent_param(self.kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(**{f"{parent_field}__pk": parent_value})
        return queryset
    
    def create(self, request, *args, **kwargs):
        parent_field, parent_value = self._get_parent_param(self.kwargs)
        request.data[parent_field] = parent_value
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        parent_field, parent_value = self._get_parent_param(self.kwargs) 
        request.data[parent_field] = parent_value
        return super().update(request, *args, **kwargs)


class ClientRootAdminViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = ClientM.objects.all()
    serializer_class = ClientRootAdminSerialzier
    permission_classes = [IsAdminUser]


class ClientUserViewSet(NestedGenericViewSet, mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = ClientUserM.objects.all()
    serializer_class = ClientUserSerializer
    permission_classes = [IsAdminUser]
