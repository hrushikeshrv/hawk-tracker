import boto3
import datetime
import logging

from django.http import HttpResponse
from django.conf import settings
from django.db.models import Min
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from api.serializers import PageSerializer, PushSerializer
from core.models import Page, Watchlist, Push
from core.utils import create_jobs_and_notify

logger = logging.getLogger('django')


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class RecentJobCountView(APIView):
    def get(self, request):
        ten_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)
        pushes = Push.objects.filter(time__gte=ten_days_ago).values('time__date').annotate(first_id=Min('id'))
        recent_pushes = Push.objects.filter(id__in=[p['first_id'] for p in pushes])
        n_jobs = []
        dates = []
        for push in recent_pushes:
            if push.n_jobs_found > 0:
                n_jobs.append(push.n_jobs_found)
                dates.append(push.time.strftime("%Y-%m-%d %H:%M"))
            else:
                try:
                    n_jobs.append(len(push.data['jobs']))
                    dates.append(push.time.strftime("%Y-%m-%d %H:%M"))
                except:
                    pass
        n_jobs.reverse()
        dates.reverse()
        return Response({"x": dates, "y": n_jobs}, status=status.HTTP_200_OK)


class PageListView(APIView):
    """
    When a request comes in to this endpoint, push all pages we have
    into the SQS queue
    """
    def chunked(self, iterable, size):
        """
        Yield successive chunks from iterable of length `size`.
        """
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    def get(self, request):
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        # In debug mode, just return the pages here, don't push to SQS
        if settings.DEBUG:
            return Response(serializer.data, status=status.HTTP_200_OK)

        api_key = request.headers.get('X-API-Key')
        if api_key != settings.HAWK_API_KEY:
            return Response({"status": "error", "cause": "Invalid API key"}, status=status.HTTP_403_FORBIDDEN)

        sqs = boto3.client("sqs", region_name='ap-south-1')
        queue_url = 'https://sqs.ap-south-1.amazonaws.com/151345839462/HawkTrackerQueue'

        data = serializer.data
        n_pages = 0
        n_messages = 0
        # An empty Push object. Jobs found from this SQS message should be
        # associated with this Push object.
        push = Push.objects.create()
        for chunk in self.chunked(data, 10):
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({'data': chunk, 'push_id': push.id}),
            )
            n_messages += 1
            n_pages += len(chunk)

        return Response({'status': 'success', 'page_count': n_pages, 'message_count': n_messages}, status=status.HTTP_200_OK)


class PushCreateView(APIView):
    def post(self, request):
        # Note: This view does not require request origin verification
        # because this view is only called during testing. The production
        # Lambda function sends requests to the PushUpdateView to update
        # and existing Push object and not create a new Push.
        serializer = PushSerializer(data=request.data)
        if serializer.is_valid():
            push = serializer.save()
            push.n_jobs_found = push.data['n_jobs_found']
            push.n_errors = push.data['n_errors']
            push.save()
            # Delete old pushes if we have more than 3000 pushes
            total_pushes = Push.objects.count()
            if total_pushes > 3000:
                logger.info("Total pushes found: {}".format(total_pushes))
                last_push = Push.objects.last()
                logger.info(f"Deleting last push {last_push}")
                last_push.delete()
            # TODO: turn this into a celery task and run asynchronously
            create_jobs_and_notify(serializer.data['data']['jobs'], push.id)
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PushUpdateView(APIView):
    def post(self, request):
        data = request.data.get('data', {'data': {}})
        logger.info(f"Received Push update with data: {data}")
        data = data['data']
        if not data:
            logger.warning(f"Received Push with no data. Got the following body: {request.data}")
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        push = Push.objects.get(id=data['push_id'])
        if push.data is None or not isinstance(push.data, dict):
            push.data = {'jobs': [], 'errors': [], 'n_errors': 0, 'n_jobs_found': 0, 'timestamp': str(data['timestamp'])}
        if 'jobs' not in push.data:
            push.data['jobs'] = []
        if 'errors' not in push.data:
            push.data['errors'] = []
        push.data['jobs'].extend(data['jobs'])
        push.data['errors'].extend(data['errors'])
        push.n_jobs_found += len(data['jobs'])
        push.n_errors += len(data['errors'])
        push.save()
        logger.info(f"Push {push.id} updated. Creating new jobs and notifying users.")
        create_jobs_and_notify(push.data['jobs'], push.id)
        return Response({}, status=status.HTTP_200_OK)


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
