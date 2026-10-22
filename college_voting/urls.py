"""
college_voting URL Configuration.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as account_views

urlpatterns = [
    # Built-in Django Admin Interface
    path('django-admin/', admin.site.urls),

    # Public Pages
    path('', account_views.home_view, name='public_home'),
    path('about/', account_views.about_view, name='public_about'),
    path('contact/', account_views.contact_view, name='public_contact'),

    # Application URLs
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('elections.dashboard_urls', namespace='dashboard')),
    path('elections/', include('elections.urls', namespace='elections')),
    path('voting/', include('voting.urls', namespace='voting')),
    path('results/', include('results.urls', namespace='results')),
]

# Helper for direct named shortcuts
urlpatterns += [
    path('home/', account_views.home_view, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site branding
admin.site.site_header = "Apex College Voting Administration"
admin.site.site_title = "College Voting Portal"
admin.site.index_title = "System Management Console"
