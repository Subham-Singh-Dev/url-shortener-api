from django.db import models
from django.utils import timezone

import string 
import random

def generate_short_code():
    """Generate unique 6-character alphanumeric code."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))


class URL(models.Model):
    """
    Core URL mapping model.
    
    Design decisions:
    - short_code: 6 chars = 62^6 = 56 billion combinations
    - click_count: denormalised counter for O(1) analytics read
    - created_at: for TTL expiry logic in future
    """
    original_url = models.URLField(max_length=2000)
    short_code   = models.CharField(
        max_length=10,
        unique=True,
        default=generate_short_code,
        db_index=True          # fast lookup on redirect
    )
    created_at   = models.DateTimeField(default=timezone.now)
    click_count  = models.PositiveIntegerField(default=0)
    is_active    = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_code} → {self.original_url[:50]}"


class Click(models.Model):
    """
    Analytics: one row per click.
    
    Design decision: separate Click model instead of
    just incrementing counter — allows time-based analytics
    (clicks per day, per hour) without extra queries.
    """
    url         = models.ForeignKey(
        URL,
        on_delete=models.CASCADE,
        related_name='clicks'
    )
    clicked_at  = models.DateTimeField(default=timezone.now)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"