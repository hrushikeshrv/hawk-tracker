from dataclasses import dataclass


@dataclass
class Page:
    name: str
    company: str
    url: str
    selector: str


@dataclass
class Job:
    """A job posting found on a page"""
    title: str
    company: str
    page: Page
    last_seen: str
    job_id: str
