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
    class Meta:
        ordering = ['-last_seen']

    title = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True, help_text='URL of the job posting, if available')
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
    class Meta:
        ordering = ['-date']

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='notifications')
    date = models.DateTimeField(auto_now_add=True)
    jobs = models.ManyToManyField(Job, related_name='notifications', blank=True)
    n_new_jobs = models.IntegerField(default=0)

    def __str__(self):
        return f'Found {self.n_new_jobs} new jobs on {self.date.strftime("%d %b, %Y, %I:%M:%S %p")}'


class Push(models.Model):
    """A push from the Lambda function about changed pages"""
    class Meta:
        verbose_name_plural = "Pushes"

    time = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f'Push at {self.time.strftime("%d %b, %Y, %I:%M:%S %p")}'


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
    RESPONSE_TYPES = [
        ('html', 'HTML'),
        ('json', 'JSON'),
    ]
    name = models.CharField(max_length=50)
    api_url = models.URLField(blank=True, null=True, help_text='If the response type is JSON, this is the URL to the API endpoint that returns the list of jobs. If the response type is HTML, this field is not used.')
    url = models.URLField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='pages')
    location = models.CharField(max_length=64, default='', null=True, blank=True)
    is_remote = models.BooleanField(default=False, blank=True, null=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0, blank=True)
    level = models.CharField(max_length=10, choices=JOB_LEVELS, default='unspec', blank=True)

    response_type = models.CharField(max_length=10, choices=RESPONSE_TYPES, default='html', blank=True)
    selector = models.CharField(max_length=128, help_text='If the response type is HTML, this is the CSS selector that selects all the job titles. If the response type is JSON, this is a comma-separated list of keys that would return the list of job titles from the JSON response.')
    title_key = models.CharField(max_length=32, help_text='If the response type is JSON, this is the key that contains the job title in a Job object in the JSON response.', blank=True, null=True)
    job_id_key = models.CharField(max_length=32, help_text='If the response type is JSON, this is the key that contains the job ID in a Job object in the JSON response.', blank=True, null=True)

    def __str__(self):
        return self.name


class Watchlist(models.Model):
    """A list of pages to watch for a user"""
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, default='')
    pages = models.ManyToManyField(Page, related_name='watchlists')
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='created_watchlists')
    subscribers = models.ManyToManyField("users.User", related_name='watchlists', blank=True)

    def __str__(self):
        return f'Watchlist {self.name} by {self.owner.username}'
