import requests
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from AHApps.artist.models import Artist, ArtistProfile,ArtistCatalogue,ArtistCatalogueCategory


def base(request):
    # Fetch all catalogues without pagination
    catalogues = ArtistCatalogue.objects.all()  
    
    return render(request, 'web/base.html', {'catalogues': catalogues})

def catalogue_detail(request, catalogue_id):
    artist_catalog = ArtistCatalogue.objects.filter(artist_catalogue_id=catalogue_id).prefetch_related('categories').first()

    context = {
        'catalog': artist_catalog,
        'categories': artist_catalog.categories.all() if artist_catalog else []
    }
    print(context) 
    return render(request, "web/catalogue_detail.html", context)

def search_images(request):
    if 'query' in request.GET:
        query = request.GET['query']
        url = f'https://www.wikiart.org/en/API/2.0/Search?key=fadd9080879c4fc2&secret=ac1d0dda16ef1012&query={query}'
        response = requests.get(url)
        data = response.json()
        images = data.get('data', [])  # Extract the images from the API response
    else:
        images = []

    return render(request, 'web/art.html', {'images': images})

def home(request):
    catalogues = ArtistCatalogue.objects.all()[12:]  # Fetch all catalogues
    return render(request, 'web/home.html', {'catalogues': catalogues})
