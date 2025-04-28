from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A custom user model"""
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
