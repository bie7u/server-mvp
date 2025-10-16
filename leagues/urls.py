from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeagueViewSet, SeasonViewSet, TeamViewSet,
    MatchViewSet, StandingViewSet
)

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'standings', StandingViewSet, basename='standing')

urlpatterns = [
    path('', include(router.urls)),
]
