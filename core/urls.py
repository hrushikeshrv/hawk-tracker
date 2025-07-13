from django.urls import path

from core.views import (
    test_view,
    HomepageView,
    WatchlistCreateView,
    WatchlistDetailView,
    WatchlistListView,
)

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),
    path('watchlists/create', WatchlistCreateView.as_view(), name='watchlist_create'),
    path('watchlists/<int:pk>', WatchlistDetailView.as_view(), name='watchlist_detail'),
    path('watchlists/explore', WatchlistListView.as_view(), name='watchlist_list'),
]
