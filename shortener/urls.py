from django.urls import path
from . import views

urlpatterns = [

    # Frontend landing page
    path('', views.home_view, name='home'),

    # Core API
    path('api/shorten/', views.ShortenURLView.as_view(), name='shorten'),

    path('api/urls/', views.ShortenURLView.as_view(), name='url-list-test'),


    # AnalyticsNote: 'top/' must come before '<str:short_code>/' so it isn't treated as a code)
    path('api/analytics/top/', views.TopURLsView.as_view(), name='analytics-top'),
    path('api/analytics/<str:short_code>/', views.URLAnalyticsView.as_view(), name='analytics-detail'),

    path('api/stats/<str:short_code>/', views.URLAnalyticsView.as_view(), name='url-stats-test'),

    # Redirect endpoint
    path('<str:short_code>/', views.RedirectView.as_view(), name='redirect'),
]