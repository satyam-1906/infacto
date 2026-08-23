from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This sends any URL starting with /api/ to your registrations app
    path('api/', include('registrations.urls')), 
]

# Always serve media files locally (payment screenshots visible in admin panel)
# In production, your web server (nginx/apache) should handle /media/ instead
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)