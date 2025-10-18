from users.models import ClientM, ClientUserM
from django.contrib.auth.models import User
from django.db.models import Sum
from django_cron import CronJobBase, Schedule
from predictions.models import PredictionM, ClientRankingM, ClientRankingEntryM
from predictions.helpers import update_client_rankings, update_predictions_status

class UpdateClientRankingsCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=60)  # Run every hour
    code = 'predictions.update_client_rankings_cron_job'

    def do(self):
        update_client_rankings()


def get_winner(home, away):
    if home > away:
        return 'home'
    elif home < away:
        return 'away'
    else:
        return 'draw'


class UpdatePredictionsStatusCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=60)  # Run every hour
    code = 'predictions.update_predictions_status_cron_job'  # Unique code

    def do(self):
        update_predictions_status()
