from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

# Define your urlpatterns without i18n_patterns or internationalization-related imports
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ramjeet.urls')),
    path('', include('ramjeet.urls'), name="ramjeet"),
]

# Add static media URL serving in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
