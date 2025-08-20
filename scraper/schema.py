"""
Dataclasses emulating the DB schema on the server
"""
from dataclasses import dataclass


@dataclass
class Page:
    """A Page object received from the server"""
    id: int
    name: str
    company: str
    company_id: int
    url: str
    selector: str
    response_type: str = 'html'
    title_key: str = ''
    job_id_key: str = ''
    job_url_key: str = ''
    api_url: str = ''


@dataclass
class Job:
    """A job posting found on a page"""
    title: str
    company: str
    company_id: int
    page: Page
    last_seen: str
    job_id: str
    url: str = ''


@dataclass
class ScrapeError:
    """An error encountered while scraping a page"""
    page: Page
    error: str
