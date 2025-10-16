from django.db import models


class League(models.Model):
    """
    Represents a football league/competition
    """
    api_id = models.IntegerField(unique=True, help_text="ID from football-data.org API")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, blank=True, null=True)
    area_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Season(models.Model):
    """
    Represents a season of a league
    """
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    api_id = models.IntegerField(help_text="ID from football-data.org API")
    start_date = models.DateField()
    end_date = models.DateField()
    current_matchday = models.IntegerField(default=1)
    winner = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['league', 'start_date']

    def __str__(self):
        return f"{self.league.name} {self.start_date.year}/{self.end_date.year}"


class Team(models.Model):
    """
    Represents a football team
    """
    api_id = models.IntegerField(unique=True, help_text="ID from football-data.org API")
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    tla = models.CharField(max_length=10, blank=True, null=True, help_text="Three Letter Abbreviation")
    crest = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Match(models.Model):
    """
    Represents a match in a league
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('TIMED', 'Timed'),
        ('IN_PLAY', 'In Play'),
        ('PAUSED', 'Paused'),
        ('FINISHED', 'Finished'),
        ('SUSPENDED', 'Suspended'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
        ('AWARDED', 'Awarded'),
    ]

    api_id = models.IntegerField(unique=True, help_text="ID from football-data.org API")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='matches')
    utc_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    matchday = models.IntegerField(help_text="Round/matchday number")
    stage = models.CharField(max_length=50, blank=True, null=True)
    group = models.CharField(max_length=50, blank=True, null=True)
    
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    
    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)
    
    winner = models.CharField(max_length=50, blank=True, null=True)
    duration = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['utc_date', 'matchday']
        indexes = [
            models.Index(fields=['season', 'matchday']),
            models.Index(fields=['utc_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} - Matchday {self.matchday}"


class Standing(models.Model):
    """
    Represents a team's standing in a league table
    """
    STANDING_TYPE_CHOICES = [
        ('TOTAL', 'Total'),
        ('HOME', 'Home'),
        ('AWAY', 'Away'),
    ]

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
    standing_type = models.CharField(max_length=10, choices=STANDING_TYPE_CHOICES, default='TOTAL')
    group = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['season', 'standing_type', 'position']
        unique_together = ['season', 'team', 'standing_type', 'group']
        indexes = [
            models.Index(fields=['season', 'standing_type', 'position']),
        ]

    def __str__(self):
        return f"{self.team.name} - Position {self.position} ({self.standing_type})"
