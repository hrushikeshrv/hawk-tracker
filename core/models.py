from django.db import models


class Company(models.Model):
    """A company whose pages will be watched"""
    class Meta:
        verbose_name_plural = "Companies"

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Job(models.Model):
    """A job posting found on a page"""
    title = models.CharField(max_length=200)
    push = models.ForeignKey('Push', on_delete=models.CASCADE, related_name='jobs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    page = models.ForeignKey('Page', on_delete=models.CASCADE, related_name='jobs')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    job_id = models.CharField(max_length=20, null=True, blank=True, help_text='Job ID extracted from the posting, if available')

    def __str__(self):
        return f'{self.title} at {self.company.name}'


class Notification(models.Model):
    """A notification for a user about a watchlist change"""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='notifications')


class Push(models.Model):
    """A push from the Lambda function about changed pages"""
    class Meta:
        verbose_name_plural = "Pushes"

    time = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()


class Page(models.Model):
    """A page on a company website that will be watched"""
    JOB_LEVELS = [
        ('unspec', 'Unspecified'),
        ('intern', 'Intern'),
        ('entry', 'Entry-level'),
        ('junior', 'Junior'),
        ('mid', 'Mid-level'),
        ('senior', 'Senior'),
        ('c_level', 'C-level'),
    ]
    name = models.CharField(max_length=30)
    url = models.URLField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='pages')
    location = models.CharField(max_length=64, default='', null=True, blank=True)
    is_remote = models.BooleanField(default=False, blank=True, null=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0, blank=True)
    level = models.CharField(max_length=10, choices=JOB_LEVELS, default='unspec', blank=True)

    selector = models.CharField(max_length=128, help_text='CSS selector that selects all job titles in the page')

    def __str__(self):
        return self.name


class Watchlist(models.Model):
    """A list of pages to watch for a user"""
    name = models.CharField(max_length=64)
    companies = models.ManyToManyField(Company, related_name='watchlists')
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='watchlists')

    def __str__(self):
        return f'Watchlist {self.name} by {self.user.username}'
