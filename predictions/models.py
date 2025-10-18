from users.models import ClientM
from django.db import models
from django.contrib.auth.models import User


from django.contrib.auth import get_user_model
from leagues.models import MatchM


# Stores a snapshot of ranking for a client at a given time
class ClientRankingM(models.Model):
	client = models.ForeignKey(ClientM, on_delete=models.CASCADE, related_name='rankings')
	created_at = models.DateTimeField(auto_now_add=True)

# Stores a user's position and points in a given client ranking
class ClientRankingEntryM(models.Model):
	ranking = models.ForeignKey(ClientRankingM, on_delete=models.CASCADE, related_name='entries')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_ranking_entries')
	points = models.IntegerField()
	position = models.IntegerField()
	class Meta:
		unique_together = ('ranking', 'user')


class PredictionM(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_CORRECT_RESULT = 'correct_result'
	STATUS_CORRECT_WINNER = 'correct_winner'
	STATUS_INCORRECT = 'incorrect'
	STATUS_LATE = 'late'
	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_CORRECT_RESULT, 'Correct Result'),
		(STATUS_CORRECT_WINNER, 'Correct Winner'),
		(STATUS_INCORRECT, 'Incorrect'),
		(STATUS_LATE, 'Late'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
	match = models.ForeignKey(MatchM, on_delete=models.CASCADE, related_name='predictions')
	predicted_home_score = models.IntegerField()
	predicted_away_score = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	points_awarded = models.IntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

	class Meta:
		unique_together = ('user', 'match')
