import sys
from pprint import pprint

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from constants import *

BASE_URL = "https://www.billboard.com/charts/hot-100/"
HTTP_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
}

_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
_year = _date.split("-")[0]
url_to_scrape = BASE_URL + _date


def perform_spotify_auth():
    spotify_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET,
                                 redirect_uri=SPOTIFY_REDIRECT_URI,
                                 scope="playlist-modify-private")
    return spotipy.Spotify(auth_manager=spotify_oauth)


def search_for_track(spotify_object, track_name):
    return spotify_object.search(q=f"track: {track_name} year: {_year}", type="track")


def create_private_playlist(spotify_object: spotipy.Spotify, name, uris):
    user_id = spotify_object.current_user()['id']
    playlist = spotify_object.user_playlist_create(user=user_id, name=name, public=False,
                                                   description="Billboard Top 100 songs")
    playlist_id = playlist['id']
    spotify_object.playlist_add_items(playlist_id=playlist_id, items=uris)


try:
    response = requests.get(url=url_to_scrape, headers=HTTP_HEADER)
    response.raise_for_status()
    billboard_web_page = response.text

    soup = BeautifulSoup(billboard_web_page, "html.parser")

    song_title_tags = soup.select(selector="li.lrv-u-width-100p h3#title-of-a-story")

    song_titles = [song_title_tag.getText().strip() for song_title_tag in song_title_tags]

    print(song_titles)

    sp = perform_spotify_auth()

    song_uris = []
    for song_title in song_titles:
        try:
            result = search_for_track(sp, song_title)
            # pprint(result)
            song_uri = result['tracks']['items'][0]['uri']
            song_uris.append(song_uri)
        except IndexError:
            print(f"{song_title} doesn't exist in Spotify. Skipped.")

    print(song_uris)
    playlist_name = f"{_date.strip()} Billboard 100"
    create_private_playlist(sp, playlist_name, song_uris)
except requests.exceptions.Timeout:
    print("The request timed out. Please try again later.")
except requests.exceptions.TooManyRedirects:
    print("Too many redirects. Check the URL and try again.")
except requests.exceptions.ConnectionError as conn_err:
    print(f"Network problem occurred: {conn_err}")
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err} (Status Code: {http_err.response.status_code})")
except requests.exceptions.RequestException as req_err:
    print(f"An unexpected error occurred: {req_err}")
