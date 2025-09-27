from django.urls import reverse
from rest_framework import serializers

from core.models import Page, Push, Job, Company


class JobSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()
    page = serializers.StringRelatedField()
    company_url = serializers.SerializerMethodField()
    page_url = serializers.SerializerMethodField()
    page_link = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'url', 'company', 'page', 'first_seen', 'last_seen', 'job_id', 'company_url', 'page_url', 'page_link']

    def get_company_url(self, obj):
        return reverse('core:company_detail', kwargs={'pk': obj.company.id})

    def get_page_url(self, obj):
        return reverse('core:page_detail', kwargs={'pk': obj.page.id})

    def get_page_link(self, obj):
        return obj.page.url


class CompanySerializer(serializers.ModelSerializer):
    company_url = serializers.HyperlinkedIdentityField(view_name='core:company_detail', lookup_field='pk')

    class Meta:
        model = Company
        fields = ['id', 'name', 'company_url']


class PageSearchSerializer(serializers.ModelSerializer):
    """
    A simplified serializer for searching pages
    """
    company = serializers.StringRelatedField()
    company_url = serializers.SerializerMethodField()
    page_url = serializers.HyperlinkedIdentityField(view_name='core:page_detail', lookup_field='pk')

    class Meta:
        model = Page
        fields = ['id', 'name', 'company', 'company_id', 'company_url', 'url', 'is_remote', 'location', 'years_of_experience', 'level', 'page_url']

    def get_company_url(self, obj):
        return reverse('core:company_detail', kwargs={'pk': obj.company.id})


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
        fields = ['time', 'data', 'n_jobs_found', 'n_errors']
