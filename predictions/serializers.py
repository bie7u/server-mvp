from rest_framework import serializers
from .models import PredictionM, ClientRankingEntryM
from django.utils import timezone
from leagues.models import MatchM


class PredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PredictionM
        fields = [
            'id', 'user', 'match', 'predicted_home_score', 'predicted_away_score',
            'created_at', 'points_awarded', 'status'
        ]
        read_only_fields = ['id', 'created_at', 'points_awarded', 'status', 'user']

    def validate(self, attrs):
        match = attrs.get('match')
        request = self.context.get('request')
        user = request.user
        if match:
            # Only allow predictions for matches with status SCHEDULED or TIMED
            if match.status not in [MatchM.SCHEDULED, MatchM.TIMED]:
                raise serializers.ValidationError('You can only predict matches with status SCHEDULED or TIMED.')
            if match.date and match.date <= timezone.now():
                raise serializers.ValidationError('You cannot predict a match that has already started.')
            # Prevent duplicate predictions for the same user and match
            if user and PredictionM.objects.filter(user=user, match=match).exists():
                raise serializers.ValidationError('You have already predicted this match.')
        return attrs
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    

class ClientRankingEntrySerializer(serializers.ModelSerializer):
	username = serializers.CharField(source='user.username', read_only=True)
	class Meta:
		model = ClientRankingEntryM
		fields = ['user', 'username', 'points', 'position']
