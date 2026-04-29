from rest_framework import serializers
from .models import URL


class URLCreateSerializer(serializers.ModelSerializer):
    """
    Input serializer — accepts original_url, returns full short URL.
    Design decision: short_code is read-only, generated server-side.
    Prevents clients from injecting arbitrary codes.
    """
    short_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = URL
        fields = ['id', 'original_url', 'short_code', 'short_url',
                  'created_at', 'click_count', 'is_active']
        read_only_fields = ['short_code', 'created_at', 'click_count',
                            'is_active']

    def get_short_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/r/{obj.short_code}/')
        return f'/r/{obj.short_code}/'


class URLAnalyticsSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for analytics endpoint.
    Exposes click_count + metadata without exposing internal id.
    """
    short_url    = serializers.SerializerMethodField()
    clicks_today = serializers.SerializerMethodField()

    class Meta:
        model  = URL
        fields = ['short_code', 'original_url', 'short_url',
                  'click_count', 'clicks_today', 'created_at', 'is_active']

    def get_short_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/r/{obj.short_code}/')
        return f'/r/{obj.short_code}/'

    def get_clicks_today(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return obj.clicks.filter(clicked_at__date=today).count()