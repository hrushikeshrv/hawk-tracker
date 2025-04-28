from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class HomepageView(TemplateView):
    template_name = 'core/index.html'
