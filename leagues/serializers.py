from rest_framework import serializers
from .models import MatchM, RoundM
from rest_framework import serializers
from .models import StandingM, StandingEntryM, LeagueM, SeasonM, TeamM


class MatchMSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    league_name = serializers.CharField(source='league.name', read_only=True)
    class Meta:
        model = MatchM
        fields = ['id', 'home_team', 'home_team_name', 'away_team', 'away_team_name', 'home_score', 'away_score', 'status', 'date', 'league', 'league_name']
        read_only_fields = fields

class RoundMSerializer(serializers.ModelSerializer):
    league_name = serializers.CharField(source='league.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    matches = MatchMSerializer(many=True, read_only=True)
    class Meta:
        model = RoundM
        fields = ['id', 'league', 'league_name', 'season', 'season_name', 'round_number', 'name', 'start_date', 'end_date', 'matches']
        read_only_fields = fields


class StandingEntryMSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    class Meta:
        model = StandingEntryM
        fields = ['id', 'team', 'team_name', 'position', 'played_games', 'won', 'draw', 'lost', 'points', 'goals_for', 'goals_against', 'goal_difference']
        read_only_fields = fields

class StandingMSerializer(serializers.ModelSerializer):
    league_name = serializers.CharField(source='league.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    entries = serializers.SerializerMethodField()

    class Meta:
        model = StandingM
        fields = ['id', 'league', 'league_name', 'season', 'season_name', 'entries']
        read_only_fields = fields

    def get_entries(self, obj):
        entries = obj.entries.order_by('position')
        return StandingEntryMSerializer(entries, many=True).data
