from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, View, CreateView, ListView

from core.models import Watchlist


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class HomepageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            watchlists = request.user.watchlists.annotate(page_count=Count('pages'))
            return render(request, 'core/dashboard.html', {
                'watchlists': watchlists,
            })
        return render(request, 'core/index.html')


class WatchlistCreateView(CreateView):
    template_name = 'core/watchlist_create.html'
    model = Watchlist
    fields = ['name', 'description']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.save()
        form.instance.subscribers.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:watchlist_detail', kwargs={'pk': self.object.pk})


class WatchlistDetailView(TemplateView):
    template_name = 'core/watchlist_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watchlist_id = self.kwargs.get('pk')
        watchlist = Watchlist.objects.select_related('owner').prefetch_related('pages', 'subscribers', 'pages__company').get(pk=watchlist_id)

        pages = watchlist.pages.all()
        paginator = Paginator(pages, 30)    # Show 30 pages per watchlist
        page_number = self.request.GET.get('page')

        try:
            paginated_pages = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_pages = paginator.page(1)
        except EmptyPage:
            paginated_pages = paginator.page(paginator.num_pages)

        context['watchlist'] = watchlist
        context['pages'] = paginated_pages
        return context


class WatchlistListView(ListView):
    template_name = 'core/watchlist_list.html'
    model = Watchlist
    paginate_by = 30
    context_object_name = 'watchlists'

    def get_queryset(self):
        queryset = super().get_queryset().annotate(page_count=Count('pages'), subscriber_count=Count('subscribers')).prefetch_related('subscribers', 'pages')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['subscribed_watchlists'] = user.watchlists.values_list('id', flat=True)
        else:
            context['subscribed_watchlists'] = []
        return context
