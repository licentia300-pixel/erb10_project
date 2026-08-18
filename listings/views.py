from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.contrib import messages
from django.urls import reverse
from .models import Wallpaper, Bookmark
from .choices import CATEGORY_CHOICES
import os


def wallpaper_list(request):
    wallpapers = Wallpaper.objects.all().order_by('-uploaded_at')

    category = request.GET.get('category')
    if category:
        wallpapers = wallpapers.filter(category=category)

    paginator = Paginator(wallpapers, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'wallpapers': page_obj,
        'page_obj': page_obj,
        'category_choices': CATEGORY_CHOICES,
    }
    return render(request, 'listings/listings.html', context)

def wallpaper_detail(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            wallpaper=wallpaper
        ).exists()

    if request.GET.get('updated'):
        back_url = request.session.get('wallpaper_back_url', reverse('listings:wallpaper_list'))
    else:
        back_url = request.META.get('HTTP_REFERER')
        if back_url:
            request.session['wallpaper_back_url'] = back_url
        else:
            back_url = reverse('listings:wallpaper_list')
            request.session['wallpaper_back_url'] = back_url

    context = {
        'wallpaper': wallpaper,
        'is_bookmarked': is_bookmarked,
        'back_url': back_url,
    }
    return render(request, 'listings/listing.html', context)


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

    return redirect(f"{reverse('listings:wallpaper_detail', args=[pk])}?updated=1")


@login_required
def bookmark_remove(request, pk):
    wallpaper = get_object_or_404(Wallpaper, pk=pk)
    Bookmark.objects.filter(user=request.user, wallpaper=wallpaper).delete()
    messages.success(request, f'"{wallpaper.title}" removed from your bookmarks.')

    referer = request.META.get('HTTP_REFERER')
    if referer and '/dashboard/' in referer:
        return redirect(referer)
    else:
        return redirect(f"{reverse('listings:wallpaper_detail', args=[pk])}?updated=1")