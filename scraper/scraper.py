"""
Scraper script to be deployed on AWS Lambda.
"""
from argparse import ArgumentParser
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
    Scrape the page at the given URL and return a list of Jobs found
    and a list of any errors encountered during scraping.
    """
    results = []
    url = page.url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    request = requests.get(url, headers=headers)
    if request.status_code != 200:
        print(f'Error: {request.status_code} for {url}')
        return ([], [ScrapeError(
            page=page,
            error=f'Error: {request.status_code} for {url}'
        )])

    if page.response_type == 'json':
        response = request.json()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        jobs = response.get(page.selector, [])
        for job in jobs:
            title = job.get(page.title_key or 'title', '').strip()
            if title:
                results.append(Job(
                    title=title,
                    company=page.company,
                    company_id=page.company_id,
                    page=page,
                    last_seen=timestamp,
                    job_id=job.get(page.job_id_key or 'id', '')
                ))
    else:
        soup = BeautifulSoup(request.content, 'html.parser')
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
    Get pages to scrape from the server, scrape those pages,
    and push scraped job data back to the server
    """
    pages = get_page_list()
    results = []
    errors = []
    if pages:
        for page in pages:
            print(f'Scraping page: {page.name} ({page.url})')
            res, err = scrape_page(page)
            results.extend(res)
            errors.extend(err)
            print(f'Found {len(res)} jobs and {len(err)} errors on {page.name}')
    push_jobs(results, errors, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    parser = ArgumentParser('Scraper script to scrape job postings from tracked pages')
    parser.add_argument(
        '-t',
        help='Test scrape a page and log the results',
        action='store_true',
    )
    parser.add_argument(
        '--url', '-u',
        help="The URL to scrape",
        type=str,
        required=False
    )
    parser.add_argument(
        '--response-type', '-r',
        help='Response type of the page to scrape (html or json)',
        type=str,
        choices=['html', 'json'],
        required=False,
        default='html',
    )
    parser.add_argument(
        '--selector', '-s',
        help='If the response type is HTML, this is the CSS selector that selects all the job titles. If the response '
             'type is JSON, this is a comma-separated list of keys that would return the list of job titles from the '
             'JSON response.',
        type=str,
        required=False,
    )
    parser.add_argument(
        '--title-key', '-tk',
        help='If the response type is JSON, this is the key that contains the job title in a Job object in the JSON '
             'response.',
        type=str,
        required=False,
    )
    parser.add_argument(
        '--job-id-key', '-jik',
        help='If the response type is JSON, this is the key that contains the job ID in a Job object in the JSON '
             'response.',
        type=str,
        required=False,
    )
    args = parser.parse_args()
    if args.t:
        if not args.url or not args.selector:
            print('Test mode requires --url and --selector arguments')
            exit(1)
        page = Page(
            name='Test Page',
            company='Test Company',
            company_id=1,
            id=1,
            url=args.url,
            selector=args.selector,
            response_type=args.response_type,
            title_key=args.title_key or '',
            job_id_key=args.job_id_key or ''
        )
        jobs, errors = scrape_page(page)
        print(f'Found {len(jobs)} jobs and {len(errors)} errors on {page.name}')
        for job in jobs:
            print(f'Job: {job.title} at {job.company}')
        for error in errors:
            print(f'Error: {error.error} on page {error.page.name}')
    else:
        main()
