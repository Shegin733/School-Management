from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin-dashboard/', include('admin_dashboard.urls')),
    path('api/librarian-dashboard/', include('librarian_dashboard.urls')),  
    path('api/staff-dashboard/', include('office_staff_dashboard.urls')),
    path('api/common/', include('common.urls')), # Admin Dashboard URL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


