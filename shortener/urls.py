from django.urls import path
from . import views

urlpatterns = [
    # Core API
    path('api/shorten/', views.ShortenURLView.as_view(), name='shorten'),

    # Redirect endpoint
    path('r/<str:short_code>/', views.RedirectView.as_view(), name='redirect'),

    # Analytics
    path('api/analytics/top/', views.TopURLsView.as_view(),    name='top-urls'),
    path('api/analytics/<str:short_code>/', views.URLAnalyticsView.as_view(), name='analytics'),
]