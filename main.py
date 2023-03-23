from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# ------------------------- Web Scraping Top 100 Music List -------------------

date_input = input("Which year do you want to travel to? Type the date in this format, YYYY-MM-DD: ")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date_input}")
data = response.text

website = BeautifulSoup(data, "html.parser")
music_titles = []
i = 0
music_names = website.select(selector="li h3", class_="c-title")
for music_name in music_names:
    if i == 100:
        break
    else:
        i += 1
        music_text = music_name.getText().strip()
        music_titles.append(music_text)

# -------------------------------- Connecting Spotify ---------------------------

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://localhost:8888/callback",
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

#  ----------------------- Searching Top Songs List on Spotify One by One --------------------------

year = date_input.split("-")[0]
song_uris = []

for title in music_titles:
    result = sp.search(q=f"track: {title} year: {year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
    except IndexError:
        pass
    else:
        song_uris.append(uri)

# ---------------------------- Creating a Playlist and Adding Songs ------------------------

playlist_id = sp.user_playlist_create(user_id, f"{date_input} Billboard 100", public=False)["id"]

sp.playlist_add_items(playlist_id, song_uris)
