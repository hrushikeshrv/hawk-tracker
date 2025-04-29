from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.serializers import PageSerializer
from core.models import Page


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class PageListView(APIView):
    def get(self, request):
        # TODO: If required, add request origin verification here
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
