from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from users.models import User


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email',]


admin.site.register(User, CustomUserAdmin)
