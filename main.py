import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.billboard.com/charts/hot-100/"
HTTP_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
}

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
url_to_scrape = BASE_URL + date

try:
    response = requests.get(url=url_to_scrape, headers=HTTP_HEADER)
    response.raise_for_status()
    billboard_web_page = response.text

    soup = BeautifulSoup(billboard_web_page, "html.parser")

    song_title_tags = soup.select(selector="li.lrv-u-width-100p h3#title-of-a-story")

    song_titles = [song_title_tag.getText().strip() for song_title_tag in song_title_tags]

    print(song_titles)

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
