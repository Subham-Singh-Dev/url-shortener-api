from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import URL, Click
from .serializers import URLCreateSerializer, URLAnalyticsSerializer


class ShortenURLView(APIView):
    """
    POST /api/shorten/
    Accepts original_url, returns short_code + short_url.

    Design: stateless, no auth required for MVP.
    Rate limiting to be added via Redis in Phase 2.
    """
    def post(self, request):
        serializer = URLCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            url_obj = serializer.save()
            return Response(
                URLCreateSerializer(
                    url_obj,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        """
        GET /api/shorten/
        Returns all shortened URLs — paginated in future.
        """
        urls = URL.objects.filter(is_active=True)
        serializer = URLCreateSerializer(
            urls,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class RedirectView(APIView):
    """
    GET /r/<short_code>/
    Core redirect — looks up short_code, logs click, redirects.

    Design: Click logged BEFORE redirect so analytics are accurate
    even if client doesn't follow the redirect.
    """
    def get(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code, is_active=True)

        # Log the click
        Click.objects.create(
            url=url_obj,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        # Increment denormalised counter — O(1) read for analytics
        URL.objects.filter(pk=url_obj.pk).update(
            click_count=url_obj.click_count + 1
        )

        return HttpResponseRedirect(url_obj.original_url)

    def _get_client_ip(self, request):
        """Extract real IP — handles proxies and load balancers."""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class URLAnalyticsView(APIView):
    """
    GET /api/analytics/<short_code>/
    Returns click count, clicks today, metadata for one URL.
    """
    def get(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code)
        serializer = URLAnalyticsSerializer(
            url_obj,
            context={'request': request}
        )
        return Response(serializer.data)


class TopURLsView(APIView):
    """
    GET /api/analytics/top/
    Returns top 10 URLs by click count.
    Design: simple ORDER BY click_count — add Redis cache here in Phase 2.
    """
    def get(self, request):
        urls = URL.objects.filter(is_active=True).order_by('-click_count')[:10]
        serializer = URLAnalyticsSerializer(
            urls,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

def home_view(request):
    """
    GET /
    Renders the landing page template.
    """
    return render(request, 'shortener/index.html')

