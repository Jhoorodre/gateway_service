from django.contrib import admin
from django.urls import path, include
from api import views as api_views  # Importe as views do app 'api'

urlpatterns = [
    path('', api_views.home, name='home'),  # Página inicial
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]
