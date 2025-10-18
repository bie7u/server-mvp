from datetime import timedelta
from django.utils import timezone
from .models import MatchM
from .serializers import MatchMSerializer
from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import StandingM
from .serializers import StandingMSerializer
from .models import RoundM
from .serializers import RoundMSerializer


# API: Upcoming matches in the next 7 days
from django_filters.rest_framework import DjangoFilterBackend

class UpcomingMatchesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	serializer_class = MatchMSerializer
	pagination_class = None  # No pagination, return all
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['league']

	def get_queryset(self):
		now = timezone.now()
		week_later = now + timedelta(days=7)
		return MatchM.objects.filter(date__gte=now, date__lte=week_later).order_by('date')
	

class RoundViewSet(mixins.ListModelMixin,
					mixins.RetrieveModelMixin,
					viewsets.GenericViewSet):
	queryset = RoundM.objects.all().order_by('round_number')
	serializer_class = RoundMSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['league', 'season']
	pagination_class = None


class StandingViewSet(mixins.ListModelMixin,
					   mixins.RetrieveModelMixin,
					   viewsets.GenericViewSet):
	queryset = StandingM.objects.all()
	serializer_class = StandingMSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['league', 'season']
	pagination_class = None
