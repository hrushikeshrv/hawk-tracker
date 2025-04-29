from django.urls import path

from api.views import (
    test_view,
    PageListView,
)

app_name = 'api'

urlpatterns = [
    path('pages/list', PageListView.as_view(), name='page-list'),
]
