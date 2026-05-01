import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import URL, Click


@pytest.mark.django_db
class TestShortenAPI:
    """Test POST /api/shorten/ endpoint."""

    def setup_method(self):
        self.client = APIClient()

    def test_shorten_valid_url_returns_201(self):
        """Valid URL returns 201 with short_code."""
        response = self.client.post('/api/shorten/', {
            'original_url': 'https://google.com'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'short_code' in response.data
        assert len(response.data['short_code']) == 6

    def test_shorten_invalid_url_returns_400(self):
        """Invalid URL returns 400."""
        response = self.client.post('/api/shorten/', {
            'original_url': 'not-a-url'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_shorten_empty_url_returns_400(self):
        """Empty URL returns 400."""
        response = self.client.post('/api/shorten/', {
            'original_url': ''
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_short_code_is_unique(self):
        """Two requests with same URL get different short codes."""
        r1 = self.client.post('/api/shorten/', {
            'original_url': 'https://google.com'
        }, format='json')
        r2 = self.client.post('/api/shorten/', {
            'original_url': 'https://google.com'
        }, format='json')
        assert r1.data['short_code'] != r2.data['short_code']

    def test_short_code_length_is_6(self):
        """Short code is always 6 characters."""
        response = self.client.post('/api/shorten/', {
            'original_url': 'https://github.com'
        }, format='json')
        assert len(response.data['short_code']) == 6

    def test_url_saved_to_database(self):
        """Shortened URL is persisted in DB."""
        self.client.post('/api/shorten/', {
            'original_url': 'https://youtube.com'
        }, format='json')
        assert URL.objects.filter(
            original_url='https://youtube.com'
        ).exists()


@pytest.mark.django_db
class TestRedirect:
    """Test GET /<short_code>/ redirect."""

    def setup_method(self):
        self.client = Client()
        self.url = URL.objects.create(
            original_url='https://github.com',
            short_code='abc123'
        )

    def test_valid_code_redirects(self):
        """Valid short code redirects to original URL."""
        response = self.client.get('/abc123/')
        assert response.status_code == 302
        assert response['Location'] == 'https://github.com'

    def test_invalid_code_returns_404(self):
        """Unknown short code returns 404."""
        response = self.client.get('/xxxxxx/')
        assert response.status_code == 404

    def test_click_recorded_on_redirect(self):
        """Each redirect creates a Click record."""
        self.client.get('/abc123/')
        assert Click.objects.filter(url=self.url).count() == 1

    def test_click_count_increments(self):
        """click_count increments on each redirect."""
        self.client.get('/abc123/')
        self.client.get('/abc123/')
        self.url.refresh_from_db()
        assert self.url.click_count == 2

    def test_inactive_url_returns_404(self):
        """Inactive URL returns 404 not redirect."""
        self.url.is_active = False
        self.url.save()
        response = self.client.get('/abc123/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestURLListAPI:
    """Test GET /api/urls/ endpoint."""

    def setup_method(self):
        self.client = APIClient()

    def test_empty_list_returns_200(self):
        """Empty database returns 200 with empty list."""
        response = self.client.get('/api/urls/')
        assert response.status_code == status.HTTP_200_OK
        assert 'urls' in response.data

    def test_returns_only_active_urls(self):
        """Inactive URLs not included in list."""
        URL.objects.create(
            original_url='https://active.com',
            short_code='act001',
            is_active=True
        )
        URL.objects.create(
            original_url='https://inactive.com',
            short_code='ina001',
            is_active=False
        )
        response = self.client.get('/api/urls/')
        urls = [u['original_url'] for u in response.data['urls']]
        assert 'https://active.com' in urls
        assert 'https://inactive.com' not in urls

    def test_response_has_correct_fields(self):
        """Each URL object has required fields."""
        URL.objects.create(
            original_url='https://test.com',
            short_code='tst001'
        )
        response = self.client.get('/api/urls/')
        if response.data['count'] > 0:
            url = response.data['urls'][0]
            assert 'short_code' in url
            assert 'original_url' in url
            assert 'click_count' in url


@pytest.mark.django_db
class TestURLStatsAPI:
    """Test GET /api/stats/<short_code>/"""

    def setup_method(self):
        self.client = APIClient()
        self.url = URL.objects.create(
            original_url='https://stats-test.com',
            short_code='stat01'
        )

    def test_stats_returns_correct_data(self):
        """Stats endpoint returns URL data."""
        response = self.client.get('/api/stats/stat01/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['short_code'] == 'stat01'
        assert response.data['original_url'] == 'https://stats-test.com'
        assert 'click_count' in response.data

    def test_stats_invalid_code_returns_404(self):
        """Invalid short code returns 404."""
        response = self.client.get('/api/stats/invalid/')
        assert response.status_code == status.HTTP_404_NOT_FOUND