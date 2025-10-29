"""
Scraper script that reads messages from the SQS queue,
scrapes the pages in the messages, and POSTs found jobs
back to the server.
"""
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import requests

from schema import Job, Page, ScrapeError

is_lambda = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

if is_lambda:
    SERVER_URL = 'https://jobs.hrus.in'
else:
    SERVER_URL = 'http://127.0.0.1:8000'


def recursive_getattr(obj: dict, attr_list: list[str], default=None):
    """
    Recursively get an attribute from a dictionary using a list of keys.
    If the attribute does not exist, return the default value.
    """
    for attr in attr_list:
        if isinstance(obj, dict) and attr in obj:
            obj = obj[attr]
        else:
            return default
    return obj


def get_page_list(page_list: list[dict] | None = None) -> list[Page]:
    """
    Get the list of pages to scrape from the Django server. Used only in test mode.
    In production the list of pages is received from SQS.
    """
    results = []
    if page_list is None:
        url = SERVER_URL + '/api/pages/list'
        request = requests.get(url)
        if request.status_code == 200:
            data = request.json()
        else:
            data = []
    else:
        data = page_list
    for page in data:
        results.append(Page(
            name=page['name'],
            company=page['company'],
            company_id=page['company_id'],
            id=page['id'],
            url=page['url'],
            api_url=page['api_url'],
            selector=page['selector'],
            response_type=page['response_type'],
            request_method=page['request_method'],
            request_payload=page.get('request_payload', {}),
            title_key=page.get('title_key', ''),
            job_id_key=page.get('job_id_key', '') or '',
            job_url_key=page.get('job_url_key', '') or '',
            job_url_prefix=page.get('job_url_prefix', '') or '',
        ))
    return results


def scrape_page(page: Page) -> tuple[list[Job], list[ScrapeError]]:
    """
    Scrape the page at the given URL and return a list of Jobs found
    and a list of any errors encountered during scraping.
    """
    results = []
    url = page.url
    if page.api_url:
        url = page.api_url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }
    if page.request_method == 'POST':
        # Specifically for Uber's careers page, which sets the CSRF token to "x"
        if page.company == 'Uber':
            headers['x-csrf-token'] = 'x'
        try:
            request = requests.post(url, headers=headers, json=page.request_payload)
        except ConnectionError:
            return ([], [ScrapeError(
                page=page,
                error=f'ConnectionError for {url}'
            )])
    elif page.request_method == 'PUT':
        try:
            request = requests.put(url, headers=headers, json=page.request_payload)
        except ConnectionError:
            return ([], [ScrapeError(
                page=page,
                error=f'ConnectionError for {url}'
            )])
    else:
        try:
            request = requests.get(url, headers=headers)
        except ConnectionError:
            return ([], [ScrapeError(
                page=page,
                error=f'ConnectionError for {url}'
            )])
    if request.status_code != 200:
        print(f'Error: {request.status_code} for {url}')
        return ([], [ScrapeError(
            page=page,
            error=f'Error: {request.status_code} for {url}'
        )])
    # Response type is JSON
    if page.response_type == 'json':
        response = request.json()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if page.selector == '':
            jobs = response
        else:
            jobs = recursive_getattr(response, page.selector.split(','), [])
        for job in jobs:
            title = recursive_getattr(job, page.title_key.split(',')).strip()
            if title:
                results.append(Job(
                    title=title,
                    company=page.company,
                    company_id=page.company_id,
                    page=page,
                    last_seen=timestamp,
                    job_id=str(recursive_getattr(job, page.job_id_key.split(','), '')).strip(),
                    url=page.job_url_prefix + str(recursive_getattr(job, page.job_url_key.split(','), ''))
                ))
    # Response type is HTML
    else:
        soup = BeautifulSoup(request.content, 'html.parser')
        elements = soup.select(page.selector)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for element in elements:
            title = element.get_text(strip=True)
            closest_a = element.find_parent('a')
            if not closest_a and element.has_attr('href'):
                closest_a = element
            job_url = ''
            if closest_a and closest_a.has_attr('href'):
                job_url = closest_a['href']
                if page.job_url_prefix:
                    job_url = page.job_url_prefix + job_url
            if title:
                results.append(Job(
                    title=title,
                    company=page.company,
                    company_id=page.company_id,
                    page=page,
                    last_seen=timestamp,
                    job_id='',
                    url=job_url,
                ))
    return results, []


def push_jobs(jobs: list[Job], errors: list[ScrapeError], timestamp: str, push_id: int = -1) -> bool:
    """
    Push scraped jobs to the server
    """
    # If we are testing locally, create a new push
    if not is_lambda:
        url = SERVER_URL + '/api/push/create'
    # Otherwise, update an existing push
    else:
        url = SERVER_URL + '/api/push/update'
    data = {
        'jobs': [],
        'timestamp': timestamp,
        'errors': [],
        'n_jobs_found': len(jobs),
        'n_errors': len(errors),
        'push_id': push_id,
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
            'url': job.url,
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
    request = requests.post(url, json={'time': timestamp, 'data': data}, headers={'X-API-Key': os.environ.get('HAWK_API_KEY')})
    return request.status_code == 200


def lambda_handler(event, context):
    """
    Get pages to scrape from the server, scrape those pages,
    and push scraped job data back to the server
    """
    push_id = -1
    if not is_lambda:
        pages = get_page_list()
    else:
        pages = []
        for record in event['Records']:
            try:
                data = json.loads(record['body'])
                pages.extend(get_page_list(data['data']))
                push_id = data['push_id']
            except json.JSONDecodeError:
                print(f'Invalid JSON body: {record["body"]}')
    results = []
    errors = []
    if pages:
        for page in pages:
            print(f'Scraping page: {page.name} ({page.url})')
            res, err = scrape_page(page)
            results.extend(res)
            errors.extend(err)
            print(f'Found {len(res)} jobs and {len(err)} errors on {page.name}\n')
    push_jobs(results, errors, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), push_id)


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
    parser.add_argument(
        '--job-url-key', '-juk',
        help='If the response type is JSON, this is the key that contains the job URL in a Job object in the JSON '
             'response.',
        type=str,
        required=False,
    )
    parser.add_argument(
        '--job-url-prefix', '-jup',
        help='If the response type is JSON and the job URL extracted from the job object is a relative URL, this prefix will be '
             'added to the job URL to make it absolute.',
        type=str,
        required=False,
        default=''
    )
    parser.add_argument(
        '--request-method', '-rm',
        help='HTTP request method to use (GET, POST, or PUT)',
        type=str,
        choices=['GET', 'POST', 'PUT'],
        required=False,
        default="GET"
    )
    parser.add_argument(
        '--request-payload', '-rp',
        help='If the request method is POST or PUT, this is the payload that will be sent with the request (in JSON format)',
        type=str,
        required=False,
        default=''
    )
    args = parser.parse_args()
    if args.t:
        if not args.url or (args.response_type == 'html' and not args.selector):
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
            request_method=args.request_method,
            request_payload=args.request_payload or None,
            title_key=args.title_key or '',
            job_id_key=args.job_id_key or '',
            job_url_key=args.job_url_key or '',
            job_url_prefix=args.job_url_prefix or '',
        )
        jobs, errors = scrape_page(page)
        print(f'Found {len(jobs)} jobs and {len(errors)} errors on {page.name}')
        for job in jobs:
            print(f'Job: {job.title} at {job.company} - {job.url}')
        for error in errors:
            print(f'Error: {error.error} on page {error.page.name}')
    else:
        lambda_handler(None, None)
