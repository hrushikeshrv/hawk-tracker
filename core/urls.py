from django.urls import path

from core.views import (
    test_view,
    HomepageView,
    WatchlistCreateView,
    WatchlistDetailView,
    WatchlistListView,
    PageDetailView,
    CompanyDetailView,
)

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),
    path('companies/<int:pk>', CompanyDetailView.as_view(), name='company_detail'),
    path('pages/<int:pk>', PageDetailView.as_view(), name='page_detail'),
    path('watchlists/create', WatchlistCreateView.as_view(), name='watchlist_create'),
    path('watchlists/<int:pk>', WatchlistDetailView.as_view(), name='watchlist_detail'),
    path('watchlists/explore', WatchlistListView.as_view(), name='watchlist_list'),
]
