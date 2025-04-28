from django.contrib import admin

from core.models import Company, Notification, Push, Page, Watchlist

admin.site.register(Company)
admin.site.register(Notification)
admin.site.register(Push)
admin.site.register(Page)
admin.site.register(Watchlist)
