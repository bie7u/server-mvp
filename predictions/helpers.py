from users.models import ClientM, ClientUserM
from django.contrib.auth.models import User
from django.db.models import Sum
from predictions.models import PredictionM, ClientRankingM, ClientRankingEntryM
from predictions.models import PredictionM
from leagues.models import MatchM


def update_client_rankings():
	for client in ClientM.objects.all():
		users = User.objects.filter(clientuserm__client=client)
		ranking_data = []
		for user in users:
			total_points = PredictionM.objects.filter(user=user, points_awarded__isnull=False).aggregate(Sum('points_awarded'))['points_awarded__sum'] or 0
			ranking_data.append({'user': user, 'points': total_points})
		ranking_data.sort(key=lambda x: x['points'], reverse=True)
		# Get or create a single ranking object per client
		ranking_obj, created = ClientRankingM.objects.get_or_create(client=client)
		# Remove old entries
		ranking_obj.entries.all().delete()
		for position, entry in enumerate(ranking_data, start=1):
			ClientRankingEntryM.objects.create(
				ranking=ranking_obj,
				user=entry['user'],
				points=entry['points'],
				position=position
			)
		print(f'Client {client.id} ranking updated with {len(ranking_data)} entries.')


def update_predictions_status():
	def get_winner(home, away):
		if home > away:
			return 'home'
		elif home < away:
			return 'away'
		else:
			return 'draw'
	predictions = PredictionM.objects.filter(
		status=PredictionM.STATUS_PENDING,
		match__status=MatchM.FINISHED,
		match__home_score__isnull=False,
		match__away_score__isnull=False
	)
	for prediction in predictions:
		match = prediction.match
		# Compare exact result
		if (prediction.predicted_home_score == match.home_score and
			prediction.predicted_away_score == match.away_score):
			prediction.status = PredictionM.STATUS_CORRECT_RESULT
			prediction.points_awarded = 3
		else:
			pred_winner = get_winner(prediction.predicted_home_score, prediction.predicted_away_score)
			match_winner = get_winner(match.home_score, match.away_score)
			if pred_winner == match_winner:
				prediction.status = PredictionM.STATUS_CORRECT_WINNER
				prediction.points_awarded = 1
			else:
				prediction.status = PredictionM.STATUS_INCORRECT
				prediction.points_awarded = None
		prediction.save(update_fields=['status', 'points_awarded'])
