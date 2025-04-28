from django.db import models


class Company(models.Model):
    """A company whose pages will be watched"""
    name = models.CharField(max_length=40)


class Notification(models.Model):
    """A notification for a user about a watchlist change"""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='notifications')


class Push(models.Model):
    """A push from the Lambda function about changed pages"""
    time = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()


class Page(models.Model):
    """A page on a company website that will be watched"""
    name = models.CharField(max_length=30)
    url = models.URLField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='pages')


class Watchlist(models.Model):
    """A list of pages to watch for a user"""
    name = models.CharField(max_length=64)
    companies = models.ManyToManyField(Company, related_name='watchlists')
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='watchlists')
