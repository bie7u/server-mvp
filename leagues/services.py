"""Service for interacting with the football-data.org API."""
import requests
from django.conf import settings
from typing import Dict, List, Optional


class FootballDataAPIClient:
    """Client for football-data.org API."""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FOOTBALL_DATA_API_KEY
        self.headers = {
            'X-Auth-Token': self.api_key
        }
    
    def get_competition(self, competition_id: int) -> Dict:
        """Get competition details."""
        url = f"{self.BASE_URL}/competitions/{competition_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_matches(self, competition_id: int, season: Optional[int] = None) -> Dict:
        """Get matches for a competition."""
        url = f"{self.BASE_URL}/competitions/{competition_id}/matches"
        params = {}
        if season:
            params['season'] = season
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_standings(self, competition_id: int, season: Optional[int] = None) -> Dict:
        """Get standings for a competition."""
        url = f"{self.BASE_URL}/competitions/{competition_id}/standings"
        params = {}
        if season:
            params['season'] = season
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_teams(self, competition_id: int, season: Optional[int] = None) -> Dict:
        """Get teams for a competition."""
        url = f"{self.BASE_URL}/competitions/{competition_id}/teams"
        params = {}
        if season:
            params['season'] = season
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
