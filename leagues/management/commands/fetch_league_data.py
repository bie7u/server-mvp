"""
Django management command to fetch league data from football-data.org API
"""
from django.core.management.base import BaseCommand, CommandError
from leagues.services import FootballDataService


class Command(BaseCommand):
    help = 'Fetch league data (matches and standings) from football-data.org API'

    def add_arguments(self, parser):
        parser.add_argument(
            'league',
            type=str,
            help='League code (e.g., PL for Premier League, PD for La Liga, BL1 for Bundesliga, SA for Serie A, FL1 for Ligue 1)'
        )
        parser.add_argument(
            '--season',
            type=int,
            help='Season year (e.g., 2024). If not provided, fetches current season data.',
            default=None
        )

    def handle(self, *args, **options):
        league_code = options['league']
        season_year = options.get('season')

        self.stdout.write(self.style.WARNING(f'Fetching data for league: {league_code}'))
        if season_year:
            self.stdout.write(self.style.WARNING(f'Season: {season_year}'))
        else:
            self.stdout.write(self.style.WARNING('Season: Current'))

        try:
            service = FootballDataService()
            result = service.save_league_data(league_code, season_year)

            self.stdout.write(self.style.SUCCESS('Successfully fetched and saved league data:'))
            self.stdout.write(self.style.SUCCESS(f'  League: {result["league"].name}'))
            self.stdout.write(self.style.SUCCESS(f'  Season: {result["season"]}'))
            self.stdout.write(self.style.SUCCESS(f'  Matches: {result["matches_count"]}'))
            self.stdout.write(self.style.SUCCESS(f'  Standings: {result["standings_count"]}'))

        except ValueError as e:
            raise CommandError(f'Configuration error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error fetching league data: {str(e)}')
