from rest_framework.response import Response
from users.models import ClientM
from .models import ClientRankingM, ClientRankingEntryM
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import mixins, viewsets, permissions
from .models import PredictionM
from .serializers import PredictionSerializer, ClientRankingEntrySerializer


class ClientRankingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	serializer_class = ClientRankingEntrySerializer
	permission_classes = [permissions.IsAuthenticated]
	pagination_class = None  # Disable pagination for rankings

	def get_queryset(self):
		user = self.request.user
		client_user = getattr(user, 'clientuserm', None)
		if not client_user or not client_user.client:
			return ClientRankingEntryM.objects.none()
		client = client_user.client
		ranking = ClientRankingM.objects.filter(client=client).first()
		if not ranking:
			return ClientRankingEntryM.objects.none()
		return ranking.entries.order_by('position')


class PredictionViewSet(mixins.CreateModelMixin,
						 mixins.ListModelMixin,
						 mixins.RetrieveModelMixin,
						 mixins.UpdateModelMixin,
						 mixins.DestroyModelMixin,
						 viewsets.GenericViewSet):
	queryset = PredictionM.objects.all()
	serializer_class = PredictionSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		if self.request.user.is_staff:
			return PredictionM.objects.all()
		return PredictionM.objects.filter(user=self.request.user)
