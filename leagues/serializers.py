"""
Serializers for leagues app
"""
from rest_framework import serializers
from .models import League, Season, Team, Match, Standing


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'api_id', 'name', 'code', 'area_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SeasonSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    league_id = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(),
        source='league',
        write_only=True
    )

    class Meta:
        model = Season
        fields = [
            'id', 'league', 'league_id', 'api_id', 'start_date', 'end_date',
            'current_matchday', 'winner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'api_id', 'name', 'short_name', 'tla', 'crest', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    season = SeasonSerializer(read_only=True)
    
    home_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='home_team',
        write_only=True
    )
    away_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='away_team',
        write_only=True
    )
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True
    )

    class Meta:
        model = Match
        fields = [
            'id', 'api_id', 'season', 'season_id', 'utc_date', 'status', 'matchday',
            'stage', 'group', 'home_team', 'home_team_id', 'away_team', 'away_team_id',
            'home_score', 'away_score', 'winner', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StandingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    season = SeasonSerializer(read_only=True)
    
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='team',
        write_only=True
    )
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True
    )

    class Meta:
        model = Standing
        fields = [
            'id', 'season', 'season_id', 'team', 'team_id', 'position',
            'played_games', 'won', 'draw', 'lost', 'points', 'goals_for',
            'goals_against', 'goal_difference', 'standing_type', 'group',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
