from django.core.management.base import BaseCommand
import requests
from leagues.models import LeagueM, SeasonM, TeamM, StandingM, StandingEntryM

API_URL = 'https://api.football-data.org/v4/competitions/2021/standings'
API_KEY = '88143b0a04a8400bab3ba1e975613f61'  # Replace with your API key

class Command(BaseCommand):
	help = 'Fetch and save Premier League standings from football-data.org'

	def handle(self, *args, **options):
		headers = {'X-Auth-Token': API_KEY}
		response = requests.get(API_URL, headers=headers)
		response.raise_for_status()
		data = response.json()

		competition = data.get('competition', {})
		league, _ = LeagueM.objects.get_or_create(
			name=competition.get('name'),
			defaults={
				'logo': competition.get('emblem', ''),
				'additional_info': f"code:{competition.get('code','')},type:{competition.get('type','')}"
			}
		)

		season_data = data.get('season', {})
		season, _ = SeasonM.objects.get_or_create(
			year=season_data.get('startDate', '')[:4],
			name=f"{competition.get('name')} {season_data.get('startDate','')[:4]}",
			league=league,
			defaults={
				'current_round_number': season_data.get('currentMatchday')
			}
		)

		standings = data.get('standings', [])
		# Create/get parent StandingM for this league/season
		standing_obj, _ = StandingM.objects.get_or_create(
			league=league,
			season=season
		)

		for standing in standings:
			table = standing.get('table', [])
			for entry in table:
				team_info = entry.get('team', {})
				team_name = team_info.get('name')
				team_obj, _ = TeamM.objects.get_or_create(name=team_name)

				entry_obj, created = StandingEntryM.objects.update_or_create(
					standing=standing_obj,
					team=team_obj,
					defaults={
						'position': entry.get('position'),
						'played_games': entry.get('playedGames'),
						'won': entry.get('won'),
						'draw': entry.get('draw'),
						'lost': entry.get('lost'),
						'points': entry.get('points'),
						'goals_for': entry.get('goalsFor'),
						'goals_against': entry.get('goalsAgainst'),
						'goal_difference': entry.get('goalDifference'),
					}
				)
				if created:
					print(f"Added standing entry for {team_name} (position {entry.get('position')})")
				else:
					print(f"Updated standing entry for {team_name} (position {entry.get('position')})")
