from django.urls import path

from api.views import (
    test_view,
    PageListView,
    PushCreateView,
    SubscribeToWatchlistView
)

app_name = 'api'

urlpatterns = [
    path('pages/list', PageListView.as_view(), name='page-list'),
    path('push/create', PushCreateView.as_view(), name='push-create'),
    path('watchlists/subscribe', SubscribeToWatchlistView.as_view(), name='watchlist-subscribe'),
]
