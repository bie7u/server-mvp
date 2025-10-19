from django.urls import path
from users.views import login_view, logout_view, refresh_token_view, me_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', refresh_token_view, name='refresh'),
    path('me/', me_view, name='me'),
]
