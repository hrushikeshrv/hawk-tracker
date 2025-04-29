import requests
from bs4 import BeautifulSoup

SERVER_URL = 'http://127.0.0.1:8000'


def get_page_list():
    """
    Get the list of pages to scrape from the Django server
    """
    url = SERVER_URL + '/api/pages/list'
    request = requests.get(url)
    if request.status_code == 200:
        return request.json()
    else:
        print(f"Error: {request.status_code}")
        return None


def scrape_page(page: dict) -> list[dict]:
    """
    Scrape the page at the given URL and return the title and content
    """
    results = []
    url = page['url']
    request = requests.get(url)
    if request.status_code != 200:
        print(f'Error: {request.status_code} for {url}')
        return []
    soup = BeautifulSoup(request.content, 'html.parser')
    # Find all elements that match the selector
    elements = soup.select(page['selector'])
    for element in elements:
        title = element.get_text(strip=True)
        if title:
            results.append({
                'title': title,
                'company': page['company'],
            })
    return results


if __name__ == '__main__':
    pages = get_page_list()
    if pages:
        for p in pages:
            print(f"Scraping {p['name']}")
            res = scrape_page(p)
            print(f'Found {len(res)} results')
    else:
        print("No pages to scrape")
