from datetime import datetime
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.models import Job, Notification
from users.models import User


def create_jobs_and_notify(jobs, push_id) -> None:
    """
    Bulk create jobs returned by the push from Lambda,
    figure out which jobs are new, and notify users watching those jobs
    TODO: Turn this into a celery task and run asynchronously
    ! This is going to be a long running function with lots of unoptimized queries
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
            url=job.get('url', ''),
        ) for job in jobs if (job['title'], job['company']) not in existing_jobs
    ]
    new_jobs = Job.objects.bulk_create(new_jobs)

    # A dictionary mapping a user's email to a list of new jobs
    notification_data = {}
    # For each new job, find the users who are watching the page.
    # There must be a better way to do this using joins
    for job in new_jobs:
        watchlists = job.page.watchlists.all().prefetch_related('subscribers')
        for watchlist in watchlists:
            for user in watchlist.subscribers.all():
                if user.pk not in notification_data:
                    notification_data[user.pk] = (user, [])
                notification_data[user.pk][1].append(job)

    notify_users(notification_data)


def notify_users(notification_data: dict[str, tuple[User, list[Job]]]) -> None:
    """
    Notify users about new jobs.
    :param notification_data: A dictionary mapping a user's primary key to a 2-tuple of
        the user's object and a list of new jobs to notify the user about
    """
    for user_pk in notification_data:
        user = notification_data[user_pk][0]
        notification = Notification.objects.create(
            user=user,
            n_new_jobs=len(notification_data[user_pk][1]),
        )
        notification.jobs.set(notification_data[user_pk][1])
        email_html = render_to_string('email/new_jobs_found.html', {
            'user': user,
            'jobs': notification_data[user_pk][1],
        })
        email_plain = strip_tags(email_html)
        from_email = 'Job Tracker <jobs@hrus.in>'
        to_email = user.email
        today = datetime.now().strftime('%d %b %Y')
        try:
            send_mail(
                subject=f'New Jobs Found on Your Watchlist - {today}',
                message=email_plain,
                html_message=email_html,
                from_email=from_email,
                recipient_list=[to_email],
            )
        except Exception as e:
            print(f'Error sending email to {to_email}: {e}')
