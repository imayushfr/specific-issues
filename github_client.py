import os
import re  # Regex
from urllib.parse import urlparse

import requests

BASE_URL = "https://api.github.com"

# Parse URL
def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url.strip())

    # Hostname is after https:// and before next /
    if parsed.hostname not in {"github.com", "www.github.com"}:
        raise ValueError("Please enter a valid GitHub repository URL.")

    # Path is after hostname
    if "//" in parsed.path:
        raise ValueError("Invalid repository URL.")

    parts = parsed.path.split("/")[:-1]
    if len(parts) < 2:
        raise ValueError("URL must include owner's and repository's name.")

    owner, repo = parts[:2]
    # Github clone URLs end with .git
    # re.sub(pattern, replacement, string)
    # In re, bare . means any character
    # r = raw str, so py doesn't treat \. as escape seq
    repo = re.sub(r"\.git$", "", repo)

    if not repo:
        raise ValueError("Invalid repository URL.")

    return owner, repo

# Make a session
def get_session():
    session = requests.Session()
    # Sets default HTTP instructions for every request in that session
    session.headers.update({
        # HTTP header: JSON response
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-03-10",
    })

# Get data from API endpoint
def github_get(session, endpoint, params=None):
    response = session.get(
        f"{BASE_URL}{endpoint}",
        params=params,  # None query ? string 
        timeout=20,
    )

    # Just specifying HTTPErrors
    if response.status_code == 404:
        raise ValueError("Repository not found or inaccessible.")

    if response.status_code == 403:
        raise ValueError("GitHub rate limit reached or access restricted.")

    if response.status_code == 429:
        raise ValueError("Try again later, too many requests.")

    # If status code is 4xx or 5xx, then raise HTTPError 
    response.raise_for_status()

    # Convert JSON response into python dicts and lists
    return response.json()

# Now doing real work
def fetch_repo(repo_url: str) -> dict:
    owner, repo = parse_repo_url(repo_url)
    session = get_session()
    # API's URLs structure
    path = f"/repos/{owner}/{repo}"

    details = github_get(session, path)

    issues = github_get(
        session, 
        f"{path}/issues",
        params={
            "state": "open",
            "per_page": 100,
            "sort": "updated",
            "direction": "desc"
        }
    )

    # Removing pull requests from issues response
    issues = [issue for issue in issues if "pull_request" not in issue]
    ## Returns dict
    languages = github_get(session, f"{path}/languages")

    return {
        "name": details["full_name"],
        "description": details.get("description"),
        "url": details["html_url"],
        "stars": details["stargazers_count"],
        "default_branch": details["default_branch"],
        "languages": languages,
        "issues": issues,
    }
