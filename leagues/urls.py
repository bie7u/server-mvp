from rest_framework.routers import DefaultRouter
from .views import StandingViewSet, RoundViewSet, UpcomingMatchesViewSet

router = DefaultRouter()
router.register(r'standings', StandingViewSet)
router.register(r'rounds', RoundViewSet)
router.register(r'upcoming-matches', UpcomingMatchesViewSet, basename='upcoming-matches')
urlpatterns = router.urls