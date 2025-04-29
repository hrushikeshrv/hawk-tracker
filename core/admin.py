from django.contrib import admin

from core.models import Company, Notification, Push, Page, Watchlist


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['company']
    list_display = ['name', 'url', 'company']
    list_filter = ['company']


admin.site.register(Notification)
admin.site.register(Push)
admin.site.register(Watchlist)
