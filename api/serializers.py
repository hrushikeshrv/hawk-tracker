from rest_framework import serializers

from core.models import Page


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['name', 'url']
