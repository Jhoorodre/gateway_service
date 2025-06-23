from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.status_check, name='status_check'),
    path('content-providers/list/', views.list_content_providers, name='list_content_providers'),
    path('content-discovery/search/', views.search_content, name='search_content'),
    path('content-discovery/filters/', views.SourceFiltersView.as_view(), name='get_source_filters'),
    path('content/item/<str:provider_id>/<str:content_id>/detail/', views.get_manga_details, name='get_manga_details'),
    path('content/item/<str:provider_id>/<str:content_id>/chapter/<str:chapter_id>/pages/', views.get_chapter_pages, name='get_chapter_pages'),
    path('image-proxy/', views.image_proxy, name='image-proxy'),
]
