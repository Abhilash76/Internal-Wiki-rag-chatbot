import requests
from bs4 import BeautifulSoup


def get_source():
    """Get the urls of all the navigable links from the pinexq documentation"""

    url = "https://docs.pinexq.net/introduction/"
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    links = soup.find_all('a')

    source = []

    for link in links:
        source_link = "https://docs.pinexq.net" + link.get('href')
        source.append(source_link)

    return source
