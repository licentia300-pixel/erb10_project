from django.db import models
from django.contrib.auth.models import User
from .choices import CATEGORY_CHOICES, FORMAT_CHOICES


class Wallpaper(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    image = models.ImageField(upload_to='wallpapers/', verbose_name="Image")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Category")
    resolution = models.CharField(max_length=50, verbose_name="Resolution")
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name="Format")
    filesize = models.CharField(max_length=50, verbose_name="File Size")
    description = models.TextField(verbose_name="Description", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_wallpapers',
        verbose_name="Uploaded By"
    )
    download_count = models.IntegerField(default=0, verbose_name="Download Count")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Wallpaper"
        verbose_name_plural = "Wallpapers"


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name="User"
    )
    wallpaper = models.ForeignKey(
        Wallpaper,
        on_delete=models.CASCADE,
        related_name='bookmarked_by',
        verbose_name="Wallpaper"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Bookmarked At")

    class Meta:
        unique_together = ('user', 'wallpaper')
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"

    def __str__(self):
        return f"{self.user.username} bookmarked {self.wallpaper.title}"