from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class HomepageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            watchlists = request.user.watchlists.all()[:10]
            return render(request, 'core/dashboard.html', {
                'watchlists': watchlists,
            })
        return render(request, 'core/index.html')
