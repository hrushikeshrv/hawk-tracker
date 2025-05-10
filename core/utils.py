from django.db.models import Q

from core.models import Job, Page, Watchlist
from users.models import User


def create_jobs_and_notify(jobs, push_id):
    """
    Bulk create jobs returned by the push from Lambda,
    figure out which jobs are new, and notify users watching those jobs
    TODO: Turn this into a celery task and run asynchronously
    """
    # Figure out which jobs are new
    job_tuples = set((job['title'], job['company']) for job in jobs)
    existing_jobs = Job.objects.filter(
        Q(
            title__in=[job[0] for job in job_tuples],
            company__name__in=[job[1] for job in job_tuples],
        )
    ).distinct().values_list('title', 'company__name')
    # Bulk create new jobs
    new_jobs = [
        Job(
            title=job['title'],
            company_id=job['company_id'],
            page_id=job['page']['id'],
            push_id=push_id,
            last_seen=job['last_seen'],
            job_id=job.get('job_id', ''),
        ) for job in jobs if (job['title'], job['company']) not in existing_jobs
    ]
    Job.objects.bulk_create(new_jobs)

    print(f'Found {len(new_jobs)} new jobs')
    print(new_jobs)

    # Find associated pages and watchlists
    updated_page_urls = [job['page']['url'] for job in new_jobs]
    updated_pages = Page.objects.filter(url__in=updated_page_urls).values_list('id', flat=True)
    updated_watchlists = Watchlist.objects.filter(page__id__in=updated_pages).distinct().values_list('id', flat=True)
    users_to_notify = User.objects.filter(watchlist__id__in=updated_watchlists).distinct()


def notify_users(notification_data):
    """
    Notify users about new jobs
    """
