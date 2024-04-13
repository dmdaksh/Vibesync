import os

import dotenv  # <- New
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import requests
from .models import YouTubeVideo
from utils import gemini_output_to_audio

# Add .env variables anywhere before SECRET_KEY
dotenv_file = os.path.join(".", ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# UPDATE secret key
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]  # Instead of your actual secret key


def index(request):
    return render(request, 'app/index.html')

def get_youtube_link(request, search_query: str):
    video, created = YouTubeVideo.objects.get_or_create(search_query=search_query)
    if not created:
        return JsonResponse({"video_link": video.video_link})
    else:
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": search_query,
            "type": "video",
            "key": YOUTUBE_API_KEY,
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        if data["items"]:
            video_id = data["items"][0]["id"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            video.video_link = video_link
            video.save()
            return JsonResponse({"video_link": video_link})
        else:
            return JsonResponse({"error": "No results found"}, status=404)


def get_yt_audio(request, yt_id: str):
    save_path = "./app/static/app/audios"
    gemini_output_to_audio(yt_id, save_path)
    return HttpResponse("Audio extracted successfully!", status=200)