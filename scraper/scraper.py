from datetime import datetime
import requests
from bs4 import BeautifulSoup

from schema import Job, Page, ScrapeError

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
                company_id=page['company_id'],
                id=page['id'],
                url=page['url'],
                selector=page['selector'],
            ))
        return results
    else:
        return None


def scrape_page(page: Page) -> tuple[list[Job], list[ScrapeError]]:
    """
    Scrape the page at the given URL and return the title and content
    """
    results = []
    url = page.url
    request = requests.get(url)
    if request.status_code != 200:
        print(f'Error: {request.status_code} for {url}')
        return ([], [ScrapeError(
            page=page,
            error=f'Error: {request.status_code} for {url}'
        )])
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
                company_id=page.company_id,
                page=page,
                last_seen=timestamp,
                job_id='',
            ))
    return results, []


def push_jobs(jobs: list[Job], errors: list[ScrapeError], timestamp: str) -> bool:
    """
    Push scraped jobs to the server
    """
    url = SERVER_URL + '/api/push/create'
    data = {
        'jobs': [],
        'timestamp': timestamp,
        'errors': []
    }
    for job in jobs:
        data['jobs'].append({
            'title': job.title,
            'company': job.company,
            'company_id': job.company_id,
            'page': {
                'id': job.page.id,
                'name': job.page.name,
                'company': job.page.company,
                'url': job.page.url,
                'selector': job.page.selector,
            },
            'last_seen': job.last_seen,
            'job_id': job.job_id,
        })

    for error in errors:
        data['errors'].append({
            'page': {
                'name': error.page.name,
                'company': error.page.company,
                'url': error.page.url,
                'selector': error.page.selector,
            },
            'error': error.error,
        })
    request = requests.post(url, json={'time': timestamp, 'data': data})
    return request.status_code == 200


def main():
    """
    Get pages from the server, scrape pages, and push scraped job data back to the server
    """
    pages = get_page_list()
    results = []
    errors = []
    if pages:
        for page in pages:
            res, err = scrape_page(page)
            results.extend(res)
            errors.extend(err)
    push_jobs(results, errors, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    main()
