import requests
from bs4 import BeautifulSoup

from schema import Job, Page

SERVER_URL = 'http://127.0.0.1:8000'


def get_page_list() -> list[Page] | None:
    """
    Get the list of pages to scrape from the Django server
    """
    url = SERVER_URL + '/api/pages/list'
    request = requests.get(url)
    if request.status_code == 200:
        results = []
        for page in request.json():
            results.append(Page(
                name=page['name'],
                company=page['company'],
                url=page['url'],
                selector=page['selector'],
            ))
        return results
    else:
        return None


def scrape_page(page: Page) -> list[Job]:
    """
    Scrape the page at the given URL and return the title and content
    """
    results = []
    url = page.url
    request = requests.get(url)
    if request.status_code != 200:
        print(f'Error: {request.status_code} for {url}')
        return []
    soup = BeautifulSoup(request.content, 'html.parser')
    # Find all elements that match the selector
    elements = soup.select(page.selector)

    for element in elements:
        title = element.get_text(strip=True)
        if title:
            results.append(Job(
                title=title,
                company=page.company,
                page=page,
                last_seen='',
                job_id='',
            ))
    return results


if __name__ == '__main__':
    pages = get_page_list()
    if pages:
        for p in pages:
            print(f"Scraping {p.name}")
            res = scrape_page(p)
            print(f'Found {len(res)} results')
    else:
        print("No pages to scrape")
