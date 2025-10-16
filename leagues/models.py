from django.db import models


class League(models.Model):
    """Represents a football league/competition."""
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, null=True, blank=True)
    area_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name


class Season(models.Model):
    """Represents a season of a league."""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    api_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    current_matchday = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ('league', 'api_id')
    
    def __str__(self):
        return f"{self.league.name} - {self.start_date.year}/{self.end_date.year}"


class Team(models.Model):
    """Represents a football team."""
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    tla = models.CharField(max_length=10, null=True, blank=True)
    crest = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class Match(models.Model):
    """Represents a football match."""
    api_id = models.IntegerField(unique=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    utc_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    matchday = models.IntegerField(null=True, blank=True)
    stage = models.CharField(max_length=50, null=True, blank=True)
    group = models.CharField(max_length=50, null=True, blank=True)
    
    # Score fields
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    winner = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        ordering = ['utc_date']
    
    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} - Round {self.matchday}"


class Standing(models.Model):
    """Represents a team's standing in a season."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='standings')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='standings')
    position = models.IntegerField()
    played_games = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        unique_together = ('season', 'team')
    
    def __str__(self):
        return f"{self.team.name} - Position {self.position} ({self.season})"
