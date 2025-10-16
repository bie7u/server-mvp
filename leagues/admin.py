from django.contrib import admin
from .models import League, Season, Team, Match, Standing


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area_name', 'api_id')
    search_fields = ('name', 'code')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('league', 'start_date', 'end_date', 'current_matchday')
    list_filter = ('league',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'tla', 'api_id')
    search_fields = ('name', 'short_name', 'tla')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'matchday', 'utc_date', 'status', 'home_score', 'away_score')
    list_filter = ('season', 'status', 'matchday')
    search_fields = ('home_team__name', 'away_team__name')
    ordering = ('-utc_date',)


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('position', 'team', 'season', 'played_games', 'won', 'draw', 'lost', 'points', 'goal_difference')
    list_filter = ('season',)
    ordering = ('season', 'position')
