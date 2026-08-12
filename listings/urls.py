from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.wallpaper_list, name='wallpaper_list'),
    path('<int:pk>/', views.wallpaper_detail, name='wallpaper_detail'),
    path('<int:pk>/download/', views.wallpaper_download, name='wallpaper_download'),
    path('<int:pk>/bookmark/add/', views.bookmark_add, name='bookmark_add'),
    path('<int:pk>/bookmark/remove/', views.bookmark_remove, name='bookmark_remove'),
]