from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.contrib import messages
from .models import Wallpaper, Bookmark
from .choices import CATEGORY_CHOICES
import os


def wallpaper_list(request):
    wallpapers = Wallpaper.objects.all().order_by('-uploaded_at')

    # Category filter
    category = request.GET.get('category')
    if category:
        wallpapers = wallpapers.filter(category=category)

    # Pagination
    paginator = Paginator(wallpapers, 9)  # 9 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'wallpapers': page_obj,
        'page_obj': page_obj,
        'category_choices': CATEGORY_CHOICES,
    }
    return render(request, 'listings/listings.html', context)  # ← 改这里


def wallpaper_detail(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            wallpaper=wallpaper
        ).exists()

    context = {
        'wallpaper': wallpaper,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'listings/listing.html', context)  # ← 改这里


def wallpaper_download(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)

    # Increase download count
    wallpaper.download_count += 1
    wallpaper.save(update_fields=['download_count'])

    try:
        response = FileResponse(
            wallpaper.image.open('rb'),
            as_attachment=True,
            filename=os.path.basename(wallpaper.image.name)
        )
        return response
    except Exception:
        raise Http404("File not found")


@login_required
def bookmark_add(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)
    Bookmark.objects.get_or_create(user=request.user, wallpaper=wallpaper)
    messages.success(request, f'"{wallpaper.title}" added to your bookmarks.')
    return redirect('listings:wallpaper_detail', pk=pk)


@login_required
def bookmark_remove(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)
    Bookmark.objects.filter(user=request.user, wallpaper=wallpaper).delete()
    messages.success(request, f'"{wallpaper.title}" removed from your bookmarks.')
    return redirect('listings:wallpaper_detail', pk=pk)