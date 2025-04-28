from django.http import HttpResponse
from django.shortcuts import render


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")
