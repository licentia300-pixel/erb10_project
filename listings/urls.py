from django.urls import path
from . import views

# Namespace for reverse URL lookup in templates (e.g., {% url 'listings:listing' listing.id %})
app_name = 'listings'

urlpatterns = [
    # Main listings gallery page (supports optional ?category= filtering)
    path('', views.index, name='listings'),
    
    # Detail view for a specific wallpaper (e.g., /listings/5/)
    path('<int:listing_id>/', views.listing, name='listing'),
    
    # POST endpoint for bookmarking/unbookmarking a wallpaper
    path('bookmark/<int:listing_id>/', views.bookmark, name='bookmark'),
]