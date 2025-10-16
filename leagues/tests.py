from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from .models import League, Season, Team, Match, Standing
from .services import FootballDataService
from unittest.mock import patch, MagicMock


class LeagueModelTest(TestCase):
    def test_create_league(self):
        league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL",
            area_name="England"
        )
        self.assertEqual(str(league), "Premier League")
        self.assertEqual(league.code, "PL")


class SeasonModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL"
        )

    def test_create_season(self):
        season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=datetime(2024, 8, 1).date(),
            end_date=datetime(2025, 5, 31).date(),
            current_matchday=10
        )
        self.assertIn("Premier League", str(season))
        self.assertEqual(season.current_matchday, 10)


class TeamModelTest(TestCase):
    def test_create_team(self):
        team = Team.objects.create(
            api_id=65,
            name="Manchester City",
            short_name="Man City",
            tla="MCI"
        )
        self.assertEqual(str(team), "Manchester City")
        self.assertEqual(team.tla, "MCI")


class MatchModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL"
        )
        self.season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=datetime(2024, 8, 1).date(),
            end_date=datetime(2025, 5, 31).date()
        )
        self.home_team = Team.objects.create(
            api_id=65,
            name="Manchester City",
            short_name="Man City"
        )
        self.away_team = Team.objects.create(
            api_id=57,
            name="Arsenal",
            short_name="Arsenal"
        )

    def test_create_match(self):
        match = Match.objects.create(
            api_id=12345,
            season=self.season,
            utc_date=timezone.now(),
            status="SCHEDULED",
            matchday=10,
            home_team=self.home_team,
            away_team=self.away_team
        )
        self.assertIn("Manchester City", str(match))
        self.assertIn("Arsenal", str(match))
        self.assertEqual(match.matchday, 10)

    def test_match_with_scores(self):
        match = Match.objects.create(
            api_id=12346,
            season=self.season,
            utc_date=timezone.now(),
            status="FINISHED",
            matchday=9,
            home_team=self.home_team,
            away_team=self.away_team,
            home_score=3,
            away_score=1,
            winner="HOME_TEAM"
        )
        self.assertEqual(match.home_score, 3)
        self.assertEqual(match.away_score, 1)
        self.assertEqual(match.winner, "HOME_TEAM")


class StandingModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL"
        )
        self.season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=datetime(2024, 8, 1).date(),
            end_date=datetime(2025, 5, 31).date()
        )
        self.team = Team.objects.create(
            api_id=65,
            name="Manchester City"
        )

    def test_create_standing(self):
        standing = Standing.objects.create(
            season=self.season,
            team=self.team,
            position=1,
            played_games=10,
            won=8,
            draw=1,
            lost=1,
            points=25,
            goals_for=25,
            goals_against=8,
            goal_difference=17
        )
        self.assertEqual(standing.position, 1)
        self.assertEqual(standing.points, 25)
        self.assertIn("Manchester City", str(standing))


class FootballDataServiceTest(TestCase):
    @patch('leagues.services.requests.get')
    def test_get_competition(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': 2021,
            'name': 'Premier League',
            'code': 'PL',
            'area': {'name': 'England'}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        service = FootballDataService(api_key='test-key')
        result = service.get_competition('PL')

        self.assertEqual(result['name'], 'Premier League')
        self.assertEqual(result['code'], 'PL')

    @patch('leagues.services.requests.get')
    def test_get_matches(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'season': {
                'id': 1234,
                'startDate': '2024-08-01',
                'endDate': '2025-05-31',
                'currentMatchday': 10
            },
            'matches': []
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        service = FootballDataService(api_key='test-key')
        result = service.get_matches('PL', 2024)

        self.assertIn('season', result)
        self.assertIn('matches', result)

    def test_service_without_api_key(self):
        with self.assertRaises(ValueError):
            FootballDataService(api_key=None)
