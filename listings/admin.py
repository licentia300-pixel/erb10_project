from django.contrib import admin
from .models import Wallpaper, Bookmark


@admin.register(Wallpaper)
class WallpaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'resolution', 'format', 'filesize', 'uploaded_by', 'uploaded_at', 'download_count')
    list_filter = ('category', 'format')
    search_fields = ('title', 'description')
    list_display_links = ('id', 'title')
    readonly_fields = ('uploaded_at', 'download_count')
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'category', 'resolution', 'format', 'filesize', 'description')
        }),
        ('Meta', {
            'fields': ('uploaded_by', 'uploaded_at', 'download_count')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallpaper', 'created_at')
    list_filter = ('user', 'wallpaper__category')
    search_fields = ('user__username', 'wallpaper__title')
    list_display_links = ('id', 'user')