from django.urls import path

from api.views import (
    test_view,
    PageListView,
    PushCreateView,
    SubscribeToWatchlistView,
    RecentJobCountView,
)

app_name = 'api'

urlpatterns = [
    path('recent-job-count', RecentJobCountView.as_view(), name='recent_job_count'),
    path('pages/list', PageListView.as_view(), name='page-list'),
    path('push/create', PushCreateView.as_view(), name='push-create'),
    path('watchlists/subscribe', SubscribeToWatchlistView.as_view(), name='watchlist-subscribe'),
]
