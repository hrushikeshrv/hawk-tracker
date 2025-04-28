from django.urls import path

from core.views import (
    test_view,
    HomepageView,
)

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),
]
