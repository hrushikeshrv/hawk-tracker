from django.urls import path

from api.views import (
    test_view,
    SearchObjectsView,
    PageListView,
    PushCreateView,
    PushUpdateView,
    SubscribeToWatchlistView,
    RecentJobCountView,
)

app_name = 'api'

urlpatterns = [
    path('search', SearchObjectsView.as_view(), name='search'),
    path('recent-job-count', RecentJobCountView.as_view(), name='recent_job_count'),
    path('pages/list', PageListView.as_view(), name='page-list'),
    path('push/create', PushCreateView.as_view(), name='push-create'),
    path('push/update', PushUpdateView.as_view(), name='push-update'),
    path('watchlists/subscribe', SubscribeToWatchlistView.as_view(), name='watchlist-subscribe'),
]
