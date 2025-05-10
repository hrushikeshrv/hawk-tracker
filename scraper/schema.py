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


@dataclass
class Job:
    """A job posting found on a page"""
    title: str
    company: str
    company_id: int
    page: Page
    last_seen: str
    job_id: str


@dataclass
class ScrapeError:
    """An error encountered while scraping a page"""
    page: Page
    error: str
