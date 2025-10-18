from django.core.management.base import BaseCommand
import requests

from leagues.models import LeagueM, SeasonM, TeamM, RoundM, MatchM
from django.utils.dateparse import parse_datetime

API_URL = 'https://api.football-data.org/v4/competitions/2021/matches'

API_KEY = '88143b0a04a8400bab3ba1e975613f61'  

class Command(BaseCommand):
    help = 'Fetch and print Premier League matches from football-data.org'

    def handle(self, *args, **options):
        headers = {}
        if API_KEY:
            headers['X-Auth-Token'] = API_KEY
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

        competition = data.get('competition', {})
        print(f"Competition: {competition.get('name')} ({competition.get('code')})")
        print(f"Season: {data.get('filters', {}).get('season')}")
        print(f"Total matches: {data.get('resultSet', {}).get('count')}")

        # Get currentMatchday from the first match's season object
        matches = data.get('matches', [])
        if matches:
            current_matchday = matches[0].get('season', {}).get('currentMatchday')
            print(f"Current Matchday: {current_matchday}")

        for match in matches:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            status = match['status']
            date = match['utcDate']
            print(f"{date}: {home} {home_score} - {away_score} {away} [{status}]")

        # --- Save to DB ---
        # League
        league, _ = LeagueM.objects.get_or_create(
            name=competition.get('name')
        )

        # Season (from first match)
        season_data = matches[0].get('season', {}) if matches else {}
        season, _ = SeasonM.objects.get_or_create(
            year=season_data.get('startDate', '')[:4],
            name=f"{competition.get('name')} {season_data.get('startDate','')[:4]}",
            league=league,
            defaults={
                'current_round_number': season_data.get('currentMatchday')
            }
        )

        # Teams cache
        team_cache = {}
        # Rounds cache
        round_cache = {}

        for match in matches:
            # Teams
            for team_key in ['homeTeam', 'awayTeam']:
                team_info = match.get(team_key, {})
                team_name = team_info.get('name')
                if team_name and team_name not in team_cache:
                    team_obj, _ = TeamM.objects.get_or_create(name=team_name)
                    team_cache[team_name] = team_obj

            home_team = team_cache.get(match['homeTeam']['name'])
            away_team = team_cache.get(match['awayTeam']['name'])

            # Round
            round_number = match.get('matchday')
            round_key = (season.id, round_number)
            if round_key not in round_cache:
                round_obj, _ = RoundM.objects.get_or_create(
                    league=league,
                    season=season,
                    round_number=round_number,
                    defaults={
                        'name': f"Round {round_number}",
                        'start_date': None,
                        'end_date': None
                    }
                )
                round_cache[round_key] = round_obj
            round_obj = round_cache[round_key]

            # Match
            match_obj, created = MatchM.objects.get_or_create(
                league=league,
                season=season,
                round=round_obj,
                home_team=home_team,
                away_team=away_team,
                date=parse_datetime(match.get('utcDate')),
                defaults={
                    'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                    'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                    'status': match.get('status'),
                }
            )
            if created:
                print(f"Saved match: {home_team.name} vs {away_team.name} on {match_obj.date}")