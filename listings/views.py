from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Listing

def index(request):
    """Gallery Grid View with Category Filtering & Pagination"""
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)
    
    # Filter by category if query param exists (?category=animation)
    category = request.GET.get('category')
    if category:
        listings = listings.filter(category__iexact=category)

    # Paginate results (6 wallpapers per page)
    paginator = Paginator(listings, 6)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)

    context = {
        'listings': paged_listings,
        'current_category': category,
    }
    return render(request, 'listings/listings.html', context)


def listing(request, listing_id):
    """Single Wallpaper Detail View"""
    listing_item = get_object_or_404(Listing, pk=listing_id)
    is_bookmarked = False

    if request.user.is_authenticated:
        is_bookmarked = listing_item.bookmarks.filter(id=request.user.id).exists()

    context = {
        'listing': listing_item,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'listings/listing.html', context)


@login_required
def bookmark(request, listing_id):
    """Toggle Bookmark Status for Logged-In User"""
    if request.method == 'POST':
        listing_item = get_object_or_404(Listing, pk=listing_id)
        
        # Toggle M2M relation between User and Listing
        if listing_item.bookmarks.filter(id=request.user.id).exists():
            listing_item.bookmarks.remove(request.user)
        else:
            listing_item.bookmarks.add(request.user)

    return redirect('listings:listing', listing_id=listing_id)