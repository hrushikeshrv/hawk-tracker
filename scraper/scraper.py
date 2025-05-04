from datetime import datetime
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
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for element in elements:
        title = element.get_text(strip=True)
        if title:
            results.append(Job(
                title=title,
                company=page.company,
                page=page,
                last_seen=timestamp,
                job_id='',
            ))
    return results


def push_jobs(jobs: list[Job], timestamp: str) -> bool:
    """
    Push scraped jobs to the server
    """
    url = SERVER_URL + '/api/push/create'
    request = requests.post(url, json={'time': timestamp, 'data': jobs})
    return request.status_code == 200


def main():
    """
    Get pages from the server, scrape pages, and push scraped job data back to the server
    """
    pages = get_page_list()
    results = []
    if pages:
        for page in pages:
            res = scrape_page(page)
            results.extend(res)
    push_jobs(results, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    main()
