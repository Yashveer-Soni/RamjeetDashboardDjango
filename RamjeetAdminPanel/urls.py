from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
# Define your urlpatterns without i18n_patterns or internationalization-related imports
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('ramjeetfrontend.urls')),
    path('', RedirectView.as_view(url='/home/', permanent=False)),
    path('', include('ramjeet.urls')),
]

# Add static media URL serving in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
