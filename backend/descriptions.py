import requests
from bs4 import BeautifulSoup


def describe(mudra):
    names = {
        "Alapadmam": ("asamyuta-hasta-bharatanatyam", "Alapadma-Hasta/"),
        "Anjali": ("samyuta-hasta-bharatanatyam", "Anjali-Hasta-Bharatanatyam"),
        "Aralam": ("asamyuta-hasta-bharatanatyam", "Arala-Hasta/"),
        "Ardhachandran": ("asamyuta-hasta-bharatanatyam", "Ardhacandra-Hasta/"),
        "Ardhapathaka": ("asamyuta-hasta-bharatanatyam", "Ardhapataka-Hasta/")
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://www.natyasutraonline.com/picture-gallery/" + names[mudra][0] + "/" + names[mudra][1]
    print(url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    container = soup.find("div", class_="text-dark").text.strip()

    return container
