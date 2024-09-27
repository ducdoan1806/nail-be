from django.contrib import admin
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("nail/", include("nails.urls")),
    path("o/", include(oauth2_urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
