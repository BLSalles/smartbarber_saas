
from django.urls import path, include

from .admin_site import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('agendamento.urls')),
]
