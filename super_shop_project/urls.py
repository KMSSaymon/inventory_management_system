from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),  # Assuming this includes your app's URLs
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),  # This sets the homepage
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
