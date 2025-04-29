from rest_framework import serializers

from core.models import Page


class PageSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = Page
        fields = ['name', 'company', 'url', 'location', 'is_remote', 'years_of_experience', 'level', 'selector']
