from django.test import TestCase
from datetime import date, datetime
from django.utils import timezone
from .models import League, Season, Team, Match, Standing


class LeagueModelTest(TestCase):
    def test_create_league(self):
        league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL",
            area_name="England"
        )
        self.assertEqual(str(league), "Premier League")
        self.assertEqual(league.api_id, 2021)


class SeasonModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL",
            area_name="England"
        )
    
    def test_create_season(self):
        season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=date(2023, 8, 1),
            end_date=date(2024, 5, 31),
            current_matchday=10
        )
        self.assertEqual(season.league, self.league)
        self.assertEqual(season.current_matchday, 10)


class TeamModelTest(TestCase):
    def test_create_team(self):
        team = Team.objects.create(
            api_id=100,
            name="Arsenal FC",
            short_name="Arsenal",
            tla="ARS",
            crest="https://example.com/crest.png"
        )
        self.assertEqual(str(team), "Arsenal FC")
        self.assertEqual(team.tla, "ARS")


class MatchModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL",
            area_name="England"
        )
        self.season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=date(2023, 8, 1),
            end_date=date(2024, 5, 31)
        )
        self.home_team = Team.objects.create(
            api_id=100,
            name="Arsenal FC",
            short_name="Arsenal",
            tla="ARS"
        )
        self.away_team = Team.objects.create(
            api_id=101,
            name="Chelsea FC",
            short_name="Chelsea",
            tla="CHE"
        )
    
    def test_create_match(self):
        match = Match.objects.create(
            api_id=5000,
            season=self.season,
            home_team=self.home_team,
            away_team=self.away_team,
            utc_date=timezone.now(),
            status="FINISHED",
            matchday=10,
            home_score=2,
            away_score=1,
            winner="HOME_TEAM"
        )
        self.assertEqual(match.matchday, 10)
        self.assertEqual(match.home_score, 2)
        self.assertEqual(match.away_score, 1)
        self.assertIn("Round 10", str(match))


class StandingModelTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            api_id=2021,
            name="Premier League",
            code="PL",
            area_name="England"
        )
        self.season = Season.objects.create(
            league=self.league,
            api_id=1234,
            start_date=date(2023, 8, 1),
            end_date=date(2024, 5, 31)
        )
        self.team = Team.objects.create(
            api_id=100,
            name="Arsenal FC",
            short_name="Arsenal",
            tla="ARS"
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
            goals_for=20,
            goals_against=5,
            goal_difference=15
        )
        self.assertEqual(standing.position, 1)
        self.assertEqual(standing.points, 25)
        self.assertEqual(standing.goal_difference, 15)
        self.assertIn("Position 1", str(standing))
