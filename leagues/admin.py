from django.contrib import admin
from .models import League, Season, Team, Match, Standing


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'area_name', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['area_name']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['league', 'start_date', 'end_date', 'current_matchday', 'winner']
    search_fields = ['league__name']
    list_filter = ['league', 'start_date']
    date_hierarchy = 'start_date'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'tla', 'created_at']
    search_fields = ['name', 'short_name', 'tla']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'matchday', 'utc_date', 'status', 'home_score', 'away_score']
    search_fields = ['home_team__name', 'away_team__name']
    list_filter = ['status', 'season', 'matchday', 'utc_date']
    date_hierarchy = 'utc_date'


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ['team', 'season', 'position', 'played_games', 'won', 'draw', 'lost', 'points', 'goal_difference']
    search_fields = ['team__name', 'season__league__name']
    list_filter = ['season', 'standing_type', 'group']
    ordering = ['season', 'position']
