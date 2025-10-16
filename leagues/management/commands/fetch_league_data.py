"""Management command to fetch league data from football-data.org API."""
from django.core.management.base import BaseCommand, CommandError
from leagues.importers import FootballDataImporter


class Command(BaseCommand):
    help = 'Fetch league data from football-data.org API'

    def add_arguments(self, parser):
        parser.add_argument(
            'competition_ids',
            nargs='+',
            type=int,
            help='Competition IDs to fetch (e.g., 2021 for Premier League)',
        )
        parser.add_argument(
            '--season',
            type=int,
            help='Specific season year to fetch (e.g., 2023). If not provided, fetches current season.',
        )
        parser.add_argument(
            '--all-seasons',
            action='store_true',
            help='Fetch all available seasons for the competition',
        )

    def handle(self, *args, **options):
        competition_ids = options['competition_ids']
        season = options.get('season')
        all_seasons = options.get('all_seasons', False)
        
        importer = FootballDataImporter()
        
        for competition_id in competition_ids:
            self.stdout.write(
                self.style.SUCCESS(f'\nFetching data for competition ID: {competition_id}')
            )
            
            try:
                if all_seasons:
                    # Get competition data to fetch all seasons
                    competition_data = importer.client.get_competition(competition_id)
                    league = importer._save_league(competition_data)
                    
                    seasons = competition_data.get('seasons', [])
                    self.stdout.write(f"Found {len(seasons)} seasons")
                    
                    for season_data in seasons:
                        season_obj = importer._save_season(league, season_data)
                        importer._import_matches(competition_id, season_obj)
                        importer._import_standings(competition_id, season_obj)
                else:
                    importer.import_competition_data(competition_id, season)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully fetched data for competition {competition_id}')
                )
            except Exception as e:
                raise CommandError(f'Error fetching competition {competition_id}: {str(e)}')
