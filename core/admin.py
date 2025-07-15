from django import forms
from django.contrib import admin
import json

from core.models import Company, Job, Notification, Push, Page, Watchlist


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'last_seen', 'first_seen']
    search_fields = ['title', 'company__name']
    list_filter = ['company__name']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['company']
    list_display = ['name', 'company', 'location', 'years_of_experience', 'level']
    list_filter = ['company']


class PushModelForm(forms.ModelForm):
    data = forms.JSONField(encoder=PrettyJSONEncoder)


@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    form = PushModelForm


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_name', 'user', 'date', 'n_new_jobs']

    def notification_name(self, obj):
        return str(obj)


admin.site.register(Watchlist)
