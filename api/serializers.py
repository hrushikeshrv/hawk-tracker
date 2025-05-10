from rest_framework import serializers

from core.models import Page, Push


class PageSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = Page
        fields = [
            'id',
            'name', 'company', 'company_id', 'url', 'location', 'is_remote',
            'years_of_experience', 'level', 'selector'
        ]


class PushSerializer(serializers.ModelSerializer):
    # company = serializers.StringRelatedField()

    class Meta:
        model = Push
        fields = ['time', 'data']
