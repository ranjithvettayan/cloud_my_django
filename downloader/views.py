from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import instaloader
import requests
import re
import base64
import zipfile
import io

# Initialize Instaloader
L = instaloader.Instaloader()
INSTAGRAM_USERNAME = 'ranjithignored1one@gmail.com'
INSTAGRAM_PASSWORD = 'Instadrop@12345'

# Login to Instagram
try:
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
except instaloader.exceptions.ConnectionException:
    print("Failed to login to Instagram")

def get_shortcode_from_url(url):
    match = re.search(r'(reel|p|tv|stories)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

@api_view(['POST'])
def download_reel(request):
    url = request.data.get('url')
    shortcode = get_shortcode_from_url(url)

    if not shortcode:
        return JsonResponse({'error': 'Invalid reel URL.'})

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            return download_media(post.video_url)
        return JsonResponse({'error': 'No video found in the reel.'})
    except Exception as e:
        return JsonResponse({'error': f'Fetching reel metadata failed: {str(e)}'})

@api_view(['POST'])
def download_post(request):
    url = request.data.get('url')
    shortcode = get_shortcode_from_url(url)

    if not shortcode:
        return JsonResponse({'error': 'Invalid post URL.'})

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        if post.typename == "GraphSidecar":
            media_urls = []
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    media_urls.append(node.video_url)
                else:
                    media_urls.append(node.display_url)
            # Return media URLs with content
            return download_multiple_media(media_urls)
        elif post.is_video:
            return download_media(post.video_url)
        elif post.typename == "GraphImage":
            return download_media(post.url)
        return JsonResponse({'error': 'No video or image found in the post.'})
    except Exception as e:
        return JsonResponse({'error': f'Fetching post metadata failed: {str(e)}'})

@api_view(['POST'])
def download_story(request):
    url = request.data.get('url')
    username, story_id = extract_story_info(url)

    if not username or not story_id:
        return JsonResponse({'error': 'Invalid story URL.'})

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        stories = L.get_stories(userids=[profile.userid])

        for story in stories:
            for item in story.get_items():
                if str(item.mediaid) == story_id:
                    media_url = item.video_url if item.is_video else item.url
                    return download_media(media_url)

        return JsonResponse({'error': 'Story not found.'})
    except Exception as e:
        return JsonResponse({'error': f'Fetching story metadata failed: {str(e)}'})

def extract_story_info(url):
    pattern = r"https://www\.instagram\.com/stories/([^/]+)/(\d+)"
    match = re.match(pattern, url)
    if match:
        username = match.group(1)
        story_id = match.group(2)
        return username, story_id
    return None, None

def download_media(media_url):
    try:
        response = requests.get(media_url, stream=True)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        response_content = HttpResponse(response.content, content_type=content_type)
        response_content['Content-Disposition'] = f'attachment; filename="{media_url.split("/")[-1]}"'

        return response_content
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)})

def download_multiple_media(media_urls):
    try:
        # Create an array to store media files and their content
        media_files = []
        
        for media_url in media_urls:
            response = requests.get(media_url, stream=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            response_content = response.content  # Get the raw content

            base64_encoded_content = base64.b64encode(response_content).decode('ascii')
            media_data = {
                'url': media_url,
                'content': base64_encoded_content,
                'content_type': content_type
            }
            media_files.append(media_data)

        # Return the media files and their content in a JSON response
        return JsonResponse({'media_files': media_files})
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}) 