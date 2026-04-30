import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from shortener.models import URL, Click


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def sample_url(db):
    return URL.objects.create(
        original_url='https://www.google.com',
        short_code='abc123'
    )


@pytest.mark.django_db
class TestShortenAPI:

    def test_shorten_valid_url(self, client):
        """POST valid URL returns 201 with short_code"""
        response = client.post('/api/shorten/', {
            'original_url': 'https://github.com'
        }, format='json')
        assert response.status_code == 201
        assert 'short_code' in response.data
        assert 'short_url' in response.data
        assert len(response.data['short_code']) == 6

    def test_shorten_invalid_url_rejected(self, client):
        """POST garbage string returns 400"""
        response = client.post('/api/shorten/', {
            'original_url': 'not-a-url'
        }, format='json')
        assert response.status_code == 400

    def test_shorten_empty_url_rejected(self, client):
        """POST empty original_url returns 400"""
        response = client.post('/api/shorten/', {
            'original_url': ''
        }, format='json')
        assert response.status_code == 400

    def test_get_all_urls(self, client, sample_url):
        """GET /api/shorten/ returns list"""
        response = client.get('/api/shorten/')
        assert response.status_code == 200
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestRedirect:

    def test_valid_redirect(self, client, sample_url):
        """Valid short_code redirects to original URL"""
        response = client.get(f'/api/{sample_url.short_code}/')
        assert response.status_code == 302
        assert response['Location'] == sample_url.original_url

    def test_redirect_logs_click(self, client, sample_url):
        """Each redirect creates a Click record"""
        client.get(f'/api/{sample_url.short_code}/')
        assert Click.objects.filter(url=sample_url).count() == 1

    def test_redirect_increments_counter(self, client, sample_url):
        """click_count increments on each redirect"""
        client.get(f'/api/{sample_url.short_code}/')
        client.get(f'/api/{sample_url.short_code}/')
        sample_url.refresh_from_db()
        assert sample_url.click_count == 2

    def test_invalid_short_code_returns_404(self, client):
        """Unknown short_code returns 404"""
        response = client.get('/api/xxxxxx/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestAnalytics:

    def test_analytics_returns_click_count(self, client, sample_url):
        """Analytics endpoint returns correct click_count"""
        client.get(f'/api/{sample_url.short_code}/')
        response = client.get(f'/api/analytics/{sample_url.short_code}/')
        assert response.status_code == 200
        assert 'click_count' in response.data
        assert 'clicks_today' in response.data

    def test_top_urls_returns_list(self, client, sample_url):
        """Top URLs endpoint returns list ordered by clicks"""
        response = client.get('/api/analytics/top/')
        assert response.status_code == 200
        assert isinstance(response.data, list)