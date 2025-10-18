from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LeagueM(models.Model):
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=200, blank=True)
    additional_info = models.CharField(max_length=1000, blank=True, null=True)


class SeasonM(models.Model):
    year = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='seasons')
    current_round_number = models.IntegerField(null=True, blank=True)


class TeamM(models.Model):
    name = models.CharField(max_length=100)


class RoundM(models.Model):
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='rounds')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.league.name} - {self.name}"


class MatchM(models.Model):
    SCHEDULED = 'SCHEDULED'
    TIMED = 'TIMED'
    IN_PLAY = 'IN_PLAY'
    PAUSED = 'PAUSED'
    FINISHED = 'FINISHED'
    SUSPENDED = 'SUSPENDED'
    POSTPONED = 'POSTPONED' 
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (SCHEDULED, 'SCHEDULED'),
        (TIMED, 'TIMED'),
        (IN_PLAY, 'IN_PLAY'),
        (PAUSED, 'PAUSED'),
        (FINISHED, 'FINISHED'),
        (SUSPENDED, 'SUSPENDED'),
        (POSTPONED, 'POSTPONED'),
        (CANCELLED, 'CANCELLED'),
    ]

    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='matches')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='matches')
    round = models.ForeignKey(RoundM, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)

    home_team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='away_matches')

    home_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    away_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')

    date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# League standings model

# Parent standings table
class StandingM(models.Model):
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='standings')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='standings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Individual team entry in standings
class StandingEntryM(models.Model):
    standing = models.ForeignKey(StandingM, on_delete=models.CASCADE, related_name='entries')
    team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='standing_entries')
    position = models.IntegerField()
    played_games = models.IntegerField()
    won = models.IntegerField()
    draw = models.IntegerField()
    lost = models.IntegerField()
    points = models.IntegerField()
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    goal_difference = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
