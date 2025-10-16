"""
Service module to interact with football-data.org API
"""
import requests
from django.conf import settings
from datetime import datetime
from typing import Optional, Dict, List
from .models import League, Season, Team, Match, Standing


class FootballDataService:
    """
    Service class to interact with football-data.org API
    """
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the service with an API key
        """
        self.api_key = api_key or getattr(settings, 'FOOTBALL_DATA_API_KEY', None)
        if not self.api_key:
            raise ValueError("Football Data API key is required. Set FOOTBALL_DATA_API_KEY in settings.")
        
        self.headers = {
            'X-Auth-Token': self.api_key
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the football-data.org API
        """
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_competition(self, competition_code: str) -> Dict:
        """
        Get competition details by code (e.g., 'PL' for Premier League)
        """
        return self._make_request(f"competitions/{competition_code}")
    
    def get_matches(self, competition_code: str, season: Optional[int] = None) -> Dict:
        """
        Get matches for a competition
        """
        params = {}
        if season:
            params['season'] = season
        return self._make_request(f"competitions/{competition_code}/matches", params)
    
    def get_standings(self, competition_code: str, season: Optional[int] = None) -> Dict:
        """
        Get standings for a competition
        """
        params = {}
        if season:
            params['season'] = season
        return self._make_request(f"competitions/{competition_code}/standings", params)
    
    def save_league_data(self, competition_code: str, season_year: Optional[int] = None):
        """
        Fetch and save league data (matches and standings) for a given competition
        
        Args:
            competition_code: The code of the competition (e.g., 'PL', 'PD', 'BL1')
            season_year: The year of the season (e.g., 2024)
        """
        # Fetch competition details
        competition_data = self.get_competition(competition_code)
        
        # Get or create league
        league, _ = League.objects.update_or_create(
            api_id=competition_data['id'],
            defaults={
                'name': competition_data['name'],
                'code': competition_data.get('code'),
                'area_name': competition_data.get('area', {}).get('name'),
            }
        )
        
        # Fetch and save matches
        matches_data = self.get_matches(competition_code, season_year)
        season = self._save_season_data(league, matches_data)
        self._save_matches(season, matches_data)
        
        # Fetch and save standings
        standings_data = self.get_standings(competition_code, season_year)
        self._save_standings(season, standings_data)
        
        return {
            'league': league,
            'season': season,
            'matches_count': season.matches.count(),
            'standings_count': season.standings.count(),
        }
    
    def _save_season_data(self, league: League, matches_data: Dict) -> Season:
        """
        Extract and save season data from matches response
        """
        season_data = matches_data.get('season', {})
        
        season, _ = Season.objects.update_or_create(
            league=league,
            api_id=season_data['id'],
            defaults={
                'start_date': datetime.fromisoformat(season_data['startDate']).date(),
                'end_date': datetime.fromisoformat(season_data['endDate']).date(),
                'current_matchday': season_data.get('currentMatchday', 1),
                'winner': season_data.get('winner', {}).get('name') if season_data.get('winner') else None,
            }
        )
        
        return season
    
    def _get_or_create_team(self, team_data: Dict) -> Team:
        """
        Get or create a team from API data
        """
        team, _ = Team.objects.update_or_create(
            api_id=team_data['id'],
            defaults={
                'name': team_data['name'],
                'short_name': team_data.get('shortName'),
                'tla': team_data.get('tla'),
                'crest': team_data.get('crest'),
            }
        )
        return team
    
    def _save_matches(self, season: Season, matches_data: Dict):
        """
        Save matches from API data
        """
        matches = matches_data.get('matches', [])
        
        for match_data in matches:
            home_team = self._get_or_create_team(match_data['homeTeam'])
            away_team = self._get_or_create_team(match_data['awayTeam'])
            
            score = match_data.get('score', {})
            full_time = score.get('fullTime', {})
            
            Match.objects.update_or_create(
                api_id=match_data['id'],
                defaults={
                    'season': season,
                    'utc_date': datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00')),
                    'status': match_data['status'],
                    'matchday': match_data['matchday'],
                    'stage': match_data.get('stage'),
                    'group': match_data.get('group'),
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': full_time.get('home'),
                    'away_score': full_time.get('away'),
                    'winner': score.get('winner'),
                    'duration': score.get('duration'),
                }
            )
    
    def _save_standings(self, season: Season, standings_data: Dict):
        """
        Save standings from API data
        """
        standings_list = standings_data.get('standings', [])
        
        for standing_group in standings_list:
            standing_type = standing_group.get('type', 'TOTAL')
            group = standing_group.get('group')
            
            for table_entry in standing_group.get('table', []):
                team = self._get_or_create_team(table_entry['team'])
                
                Standing.objects.update_or_create(
                    season=season,
                    team=team,
                    standing_type=standing_type,
                    group=group or '',
                    defaults={
                        'position': table_entry['position'],
                        'played_games': table_entry['playedGames'],
                        'won': table_entry['won'],
                        'draw': table_entry['draw'],
                        'lost': table_entry['lost'],
                        'points': table_entry['points'],
                        'goals_for': table_entry['goalsFor'],
                        'goals_against': table_entry['goalsAgainst'],
                        'goal_difference': table_entry['goalDifference'],
                    }
                )
