"""
Views for leagues app
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import League, Season, Team, Match, Standing
from .serializers import (
    LeagueSerializer, SeasonSerializer, TeamSerializer,
    MatchSerializer, StandingSerializer
)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing leagues
    """
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing seasons
    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['league', 'league__code']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing teams
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'short_name', 'tla']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing matches
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season', 'matchday', 'status', 'home_team', 'away_team']
    ordering_fields = ['utc_date', 'matchday', 'created_at']
    ordering = ['utc_date']


class StandingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing standings
    """
    queryset = Standing.objects.all()
    serializer_class = StandingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season', 'team', 'standing_type', 'group']
    ordering_fields = ['position', 'points', 'goal_difference']
    ordering = ['position']
