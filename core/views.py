from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, View, CreateView, ListView, DetailView

from core.models import Watchlist, Page, Company, Job


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class HomepageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            watchlists = request.user.watchlists.annotate(page_count=Count('pages'))
            notifications = request.user.notifications.all()
            paginator = Paginator(notifications, 3)  # Show 3 notifications per page
            page_number = request.GET.get('page')

            try:
                paginated_notifications = paginator.page(page_number)
            except PageNotAnInteger:
                paginated_notifications = paginator.page(1)
            except EmptyPage:
                paginated_notifications = paginator.page(paginator.num_pages)

            return render(request, 'core/dashboard.html', {
                'watchlists': watchlists,
                'notifications': paginated_notifications,
            })
        return render(request, 'core/index.html', {
            'num_companies': Company.objects.count(),
            'num_pages': Page.objects.count(),
            'num_jobs': Job.objects.count(),
            'recent_jobs': Job.objects.select_related('company').all()[:10],
        })


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'core/company_detail.html'
    context_object_name = 'company'

    def get_object(self, queryset=None):
        """Override to ensure the company is fetched with its related jobs."""
        return Company.objects.prefetch_related('jobs').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        jobs = company.jobs.all()
        paginator = Paginator(jobs, 30)  # Show 30 jobs per page
        page_number = self.request.GET.get('page')

        try:
            paginated_pages = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_pages = paginator.page(1)
        except EmptyPage:
            paginated_pages = paginator.page(paginator.num_pages)

        context['pages'] = paginated_pages
        return context


class CompanyListView(ListView):
    model = Company
    template_name = 'core/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().annotate(job_count=Count('jobs', distinct=True), page_count=Count('pages', distinct=True)).prefetch_related('jobs', 'pages')
        return queryset


class PageDetailView(DetailView):
    model = Page
    template_name = 'core/page_detail.html'
    context_object_name = 'page'

    def get_object(self, queryset=None):
        """Override to ensure the page is fetched with its related company."""
        return Page.objects.select_related('company').prefetch_related('jobs').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        jobs = page.jobs.all()
        paginator = Paginator(jobs, 30)      # Show 30 jobs per page
        page_number = self.request.GET.get('page')

        try:
            paginated_pages = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_pages = paginator.page(1)
        except EmptyPage:
            paginated_pages = paginator.page(paginator.num_pages)

        context['pages'] = paginated_pages
        return context


class PageListView(ListView):
    model = Page
    template_name = 'core/page_list.html'
    context_object_name = 'pages'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company').prefetch_related('jobs').annotate(job_count=Count('jobs', distinct=True))
        return queryset


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
