import pytest
from django.contrib.auth.models import User
from users.models import ClientM, ClientUserM
from leagues.models import MatchM, TeamM
from predictions.models import PredictionM, ClientRankingM, ClientRankingEntryM
from predictions.helpers import update_predictions_status, update_client_rankings
from django.utils import timezone
import datetime

# python -m pytest --ds=myproject.settings predictions/tests/
@pytest.mark.django_db
def test_update_predictions_status_does_not_update_non_pending():
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    user = User.objects.create(username='user4')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    prediction = PredictionM.objects.create(
        user=user, match=match, predicted_home_score=2, predicted_away_score=1, status=PredictionM.STATUS_CORRECT_RESULT
    )
    update_predictions_status()
    prediction.refresh_from_db()
    assert prediction.status == PredictionM.STATUS_CORRECT_RESULT
    assert prediction.points_awarded is None

@pytest.mark.django_db
def test_update_predictions_status_does_not_update_unfinished_match():
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    user = User.objects.create(username='user5')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.SCHEDULED, date=timezone.now()
    )
    prediction = PredictionM.objects.create(
        user=user, match=match, predicted_home_score=2, predicted_away_score=1
    )
    update_predictions_status()
    prediction.refresh_from_db()
    assert prediction.status == PredictionM.STATUS_PENDING
    assert prediction.points_awarded is None

@pytest.mark.django_db
def test_update_client_rankings_empty():
    client = ClientM.objects.create(name='EmptyClient', admin_name='admin', admin_email='admin@empty.com')
    update_client_rankings()
    ranking = ClientRankingM.objects.get(client=client)
    assert ranking.entries.count() == 0

@pytest.mark.django_db
def test_update_client_rankings_same_points_order():
    client = ClientM.objects.create(name='TieClient', admin_name='admin', admin_email='admin@tie.com')
    user1 = User.objects.create(username='auser')
    user2 = User.objects.create(username='buser')
    ClientUserM.objects.create(user=user1, client=client)
    ClientUserM.objects.create(user=user2, client=client)
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    PredictionM.objects.create(user=user1, match=match, predicted_home_score=2, predicted_away_score=1, points_awarded=2)
    PredictionM.objects.create(user=user2, match=match, predicted_home_score=2, predicted_away_score=1, points_awarded=2)
    update_client_rankings()
    ranking = ClientRankingM.objects.get(client=client)
    entries = list(ranking.entries.order_by('position'))
    assert entries[0].points == entries[1].points == 2
    # Order by username (alphabetical)
    assert entries[0].user.username < entries[1].user.username

@pytest.mark.django_db
def test_update_client_rankings_idempotent():
    client = ClientM.objects.create(name='IdemClient', admin_name='admin', admin_email='admin@idem.com')
    user = User.objects.create(username='idemuser')
    ClientUserM.objects.create(user=user, client=client)
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    PredictionM.objects.create(user=user, match=match, predicted_home_score=2, predicted_away_score=1, points_awarded=3)
    update_client_rankings()
    update_client_rankings()
    ranking = ClientRankingM.objects.get(client=client)
    assert ranking.entries.count() == 1

@pytest.mark.django_db
def test_update_predictions_status_correct_result():
    user = User.objects.create(username='user1')
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    prediction = PredictionM.objects.create(
        user=user, match=match, predicted_home_score=2, predicted_away_score=1
    )
    update_predictions_status()
    prediction.refresh_from_db()
    assert prediction.status == PredictionM.STATUS_CORRECT_RESULT
    assert prediction.points_awarded == 3

@pytest.mark.django_db
def test_update_predictions_status_correct_winner():
    user = User.objects.create(username='user2')
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    prediction = PredictionM.objects.create(
        user=user, match=match, predicted_home_score=3, predicted_away_score=0
    )
    update_predictions_status()
    prediction.refresh_from_db()
    assert prediction.status == PredictionM.STATUS_CORRECT_WINNER
    assert prediction.points_awarded == 1

@pytest.mark.django_db
def test_update_predictions_status_incorrect():
    user = User.objects.create(username='user3')
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    prediction = PredictionM.objects.create(
        user=user, match=match, predicted_home_score=0, predicted_away_score=3
    )
    update_predictions_status()
    prediction.refresh_from_db()
    assert prediction.status == PredictionM.STATUS_INCORRECT
    assert prediction.points_awarded is None

@pytest.mark.django_db
def test_update_client_rankings():
    client = ClientM.objects.create(name='TestClient', admin_name='admin', admin_email='admin@test.com')
    user1 = User.objects.create(username='user1')
    user2 = User.objects.create(username='user2')
    ClientUserM.objects.create(user=user1, client=client)
    ClientUserM.objects.create(user=user2, client=client)
    from leagues.models import LeagueM, SeasonM
    league = LeagueM.objects.create(name='Test League')
    season = SeasonM.objects.create(name='2025', year='2025', league=league)
    home_team = TeamM.objects.create(name='Home')
    away_team = TeamM.objects.create(name='Away')
    match = MatchM.objects.create(
        home_team=home_team,
        away_team=away_team,
        league=league,
        season=season,
        home_score=2, away_score=1, status=MatchM.FINISHED, date=timezone.now()
    )
    PredictionM.objects.create(user=user1, match=match, predicted_home_score=2, predicted_away_score=1, points_awarded=3)
    PredictionM.objects.create(user=user2, match=match, predicted_home_score=3, predicted_away_score=0, points_awarded=1)
    update_client_rankings()
    ranking = ClientRankingM.objects.get(client=client)
    entries = ranking.entries.order_by('position')
    assert entries.count() == 2
    assert entries[0].user == user1 and entries[0].points == 3 and entries[0].position == 1
    assert entries[1].user == user2 and entries[1].points == 1 and entries[1].position == 2
