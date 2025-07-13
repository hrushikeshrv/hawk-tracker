from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, View, CreateView

from core.models import Watchlist


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


class WatchlistCreateView(CreateView):
    template_name = 'core/watchlist_create.html'
    model = Watchlist
    fields = ['name',]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:watchlist_detail', kwargs={'pk': self.object.pk})


class WatchlistDetailView(TemplateView):
    template_name = 'core/watchlist_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watchlist_id = self.kwargs.get('pk')
        context['watchlist'] = Watchlist.objects.get(pk=watchlist_id)
        return context
