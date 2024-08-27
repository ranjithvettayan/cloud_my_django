from django.urls import path
from .views import download_reel, download_post, download_story

urlpatterns = [
    path('download/reel', download_reel, name='download_reel'),
    path('download/post', download_post, name='download_post'),
    path('download/story', download_story, name='download_story'),
]
