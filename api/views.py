from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.serializers import PageSerializer, PushSerializer
from core.models import Page, Watchlist
from core.utils import create_jobs_and_notify


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class PageListView(APIView):
    def get(self, request):
        # TODO: If required, add request origin verification here
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PushCreateView(APIView):
    def post(self, request):
        # TODO: If required, add request origin verification here
        serializer = PushSerializer(data=request.data)
        if serializer.is_valid():
            push = serializer.save()
            # TODO: turn this into a celery task and run asynchronously
            create_jobs_and_notify(serializer.data['data']['jobs'], push.id)
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribeToWatchlistView(APIView):
    def post(self, request):
        watchlist_id = request.data.get('watchlist_id')
        if not watchlist_id:
            return Response({"error": "Watchlist ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_authenticated:
            return Response({"error": "User must be authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            watchlist = Watchlist.objects.get(id=watchlist_id)
        except Watchlist.DoesNotExist:
            return Response({"error": "Watchlist not found."}, status=status.HTTP_404_NOT_FOUND)

        operation = request.data.get('operation', 'subscribe')
        if operation not in ['subscribe', 'unsubscribe']:
            return Response({"error": "Invalid operation. Use 'subscribe' or 'unsubscribe'."}, status=status.HTTP_400_BAD_REQUEST)
        if operation == 'unsubscribe':
            request.user.watchlists.remove(watchlist)
        else:
            request.user.watchlists.add(watchlist)
        return Response({}, status=status.HTTP_200_OK)
