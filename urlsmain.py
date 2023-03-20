from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('abode/', include("abode_app.urls")),
    path('api/', include("api_app.urls")),
    # path('abode/', include("abode_app.urls")),
    path('management/', include("management_app.urls")),
    
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
