from django.shortcuts import render
from listings.models import Wallpaper

# Create your views here.
def index(request):
    wallpapers = Wallpaper.objects.order_by('-uploaded_at')[:3]
    context = {"listings": wallpapers
            }
    return render(request,'pages/index.html', context)

def about(request):
    return render(request, 'pages/about.html')