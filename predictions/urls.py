from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PredictionViewSet, ClientRankingViewSet

router = DefaultRouter()
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'client-rankings', ClientRankingViewSet, basename='client-ranking')
urlpatterns = router.urls
