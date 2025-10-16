"""Data importers for football data."""
from datetime import datetime
from typing import Dict, List
from django.utils import timezone
from .models import League, Season, Team, Match, Standing
from .services import FootballDataAPIClient


class FootballDataImporter:
    """Imports data from football-data.org API into the database."""
    
    def __init__(self):
        self.client = FootballDataAPIClient()
    
    def import_competition_data(self, competition_id: int, season_year: int = None):
        """Import all data for a competition (league, season, matches, standings)."""
        print(f"Fetching competition data for competition ID: {competition_id}")
        
        # Get competition details
        competition_data = self.client.get_competition(competition_id)
        league = self._save_league(competition_data)
        
        # Determine which seasons to import
        if season_year:
            seasons_to_import = [s for s in competition_data.get('seasons', []) 
                                if datetime.fromisoformat(s['startDate'].replace('Z', '+00:00')).year == season_year]
        else:
            # Import current season by default
            current_season = competition_data.get('currentSeason')
            seasons_to_import = [current_season] if current_season else []
        
        for season_data in seasons_to_import:
            season = self._save_season(league, season_data)
            self._import_matches(competition_id, season)
            self._import_standings(competition_id, season)
        
        print(f"Successfully imported data for {league.name}")
    
    def _save_league(self, data: Dict) -> League:
        """Save or update league data."""
        league, created = League.objects.update_or_create(
            api_id=data['id'],
            defaults={
                'name': data['name'],
                'code': data.get('code'),
                'area_name': data.get('area', {}).get('name'),
            }
        )
        action = "Created" if created else "Updated"
        print(f"{action} league: {league.name}")
        return league
    
    def _save_season(self, league: League, data: Dict) -> Season:
        """Save or update season data."""
        start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00')).date()
        
        season, created = Season.objects.update_or_create(
            league=league,
            api_id=data['id'],
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'current_matchday': data.get('currentMatchday'),
            }
        )
        action = "Created" if created else "Updated"
        print(f"{action} season: {season}")
        return season
    
    def _save_team(self, data: Dict) -> Team:
        """Save or update team data."""
        team, _ = Team.objects.update_or_create(
            api_id=data['id'],
            defaults={
                'name': data['name'],
                'short_name': data.get('shortName'),
                'tla': data.get('tla'),
                'crest': data.get('crest'),
            }
        )
        return team
    
    def _import_matches(self, competition_id: int, season: Season):
        """Import matches for a season."""
        print(f"Importing matches for {season}")
        
        matches_data = self.client.get_matches(competition_id)
        matches = matches_data.get('matches', [])
        
        for match_data in matches:
            # Only import matches for this season
            match_season_id = match_data.get('season', {}).get('id')
            if match_season_id != season.api_id:
                continue
            
            home_team = self._save_team(match_data['homeTeam'])
            away_team = self._save_team(match_data['awayTeam'])
            
            utc_date = datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00'))
            
            score = match_data.get('score', {})
            full_time = score.get('fullTime', {})
            
            Match.objects.update_or_create(
                api_id=match_data['id'],
                defaults={
                    'season': season,
                    'home_team': home_team,
                    'away_team': away_team,
                    'utc_date': utc_date,
                    'status': match_data['status'],
                    'matchday': match_data.get('matchday'),
                    'stage': match_data.get('stage'),
                    'group': match_data.get('group'),
                    'home_score': full_time.get('home'),
                    'away_score': full_time.get('away'),
                    'winner': score.get('winner'),
                }
            )
        
        print(f"Imported {len(matches)} matches")
    
    def _import_standings(self, competition_id: int, season: Season):
        """Import standings for a season."""
        print(f"Importing standings for {season}")
        
        try:
            standings_data = self.client.get_standings(competition_id)
            standings = standings_data.get('standings', [])
            
            # Clear existing standings for this season
            Standing.objects.filter(season=season).delete()
            
            for standing_group in standings:
                table = standing_group.get('table', [])
                for entry in table:
                    team = self._save_team(entry['team'])
                    
                    Standing.objects.create(
                        season=season,
                        team=team,
                        position=entry['position'],
                        played_games=entry['playedGames'],
                        won=entry['won'],
                        draw=entry['draw'],
                        lost=entry['lost'],
                        points=entry['points'],
                        goals_for=entry['goalsFor'],
                        goals_against=entry['goalsAgainst'],
                        goal_difference=entry['goalDifference'],
                    )
            
            print(f"Imported {len(table)} standings entries")
        except Exception as e:
            print(f"Error importing standings: {e}")
