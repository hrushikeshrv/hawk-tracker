from rest_framework import serializers

from core.models import Page, Push


class PageSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = Page
        fields = [
            'id',
            'name', 'company', 'company_id', 'api_url', 'url', 'location', 'is_remote',
            'years_of_experience', 'level', 'selector', 'response_type', 'title_key', 'job_id_key',
            'job_url_key', 'job_url_prefix', 'request_method', 'request_payload'
        ]


class PushSerializer(serializers.ModelSerializer):
    # company = serializers.StringRelatedField()

    class Meta:
        model = Push
        fields = ['time', 'data']
