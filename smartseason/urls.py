"""
SmartSeason URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root → dashboard (login required, handled by view)
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Authentication (login / logout / profile)
    path('accounts/', include('accounts.urls')),

    # Dashboard + field management
    path('dashboard/', include('fields.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
