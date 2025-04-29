from django.db import models


class Company(models.Model):
    """A company whose pages will be watched"""
    class Meta:
        verbose_name_plural = "Companies"

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Watchlist(models.Model):
    """A list of pages to watch for a user"""
    name = models.CharField(max_length=64)
    companies = models.ManyToManyField(Company, related_name='watchlists')
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='watchlists')

    def __str__(self):
        return f'Watchlist {self.name} by {self.user.username}'
