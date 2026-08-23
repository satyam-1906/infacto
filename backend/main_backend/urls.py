from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This sends any URL starting with /api/ to your registrations app
    path('api/', include('registrations.urls')), 
]

# This allows Django to display your uploaded screenshots in the admin panel
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)