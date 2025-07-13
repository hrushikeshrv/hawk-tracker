from django.urls import path

from core.views import (
    test_view,
    HomepageView,
    WatchlistCreateView,
    WatchlistDetailView,
)

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),
    path('watchlist/create', WatchlistCreateView.as_view(), name='watchlist_create'),
    path('watchlist/<int:pk>', WatchlistDetailView.as_view(), name='watchlist_detail'),
]
