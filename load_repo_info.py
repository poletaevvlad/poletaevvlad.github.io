#! /bin/env python3
import os
import re
from collections import defaultdict
from pathlib import Path

import requests
import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


RE_PAGE_NUMBER = re.compile(r"(?:&|\?)page=(\d+)")


def load_repo_requests(data_dir):
    with (data_dir / "projects.yaml").open() as file:
        projects = yaml.load(file, Loader)

    return (
        (project["repo"]["owner"], project["repo"]["name"])
        for section in projects
        for project in section["projects"]
        if "repo" in project
    )


def make_request(url):
    headers = {}
    if "GITHUB_OAUTH_TOKEN" in os.environ:
        headers["Authorization"] = "token " + os.environ["GITHUB_OAUTH_TOKEN"]
    return requests.get(url, headers=headers)


def retrieve_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = make_request(url)
    if response.status_code != 200:
        content = response.content.decode("utf-8")
        raise RuntimeError("Cannot load languages: " + content)

    data = response.json()
    total_weight = sum(data.values())
    return [
        {"language": language, "weight": weight / total_weight}
        for language, weight in data.items()
    ]


def retrieve_commits_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
    response = make_request(url)
    if response.status_code != 200:
        content = response.content.decode("utf-8")
        raise RuntimeError("Cannot load commits: " + content)

    if "link" not in response.headers:
        return 0

    links = requests.utils.parse_header_links(response.headers["link"])
    for link in links:
        if "rel" in link and link["rel"] == "last":
            matches = re.search(RE_PAGE_NUMBER, link["url"])
            if matches is None:
                return 0
            return int(matches.group(1))
    return 0


def retrieve_repo_info(owner, repo):
    response = make_request(f"https://api.github.com/repos/{owner}/{repo}")
    if response.status_code != 200:
        content = response.content.decode("utf-8")
        raise RuntimeError("Repository does not exist: " + content)

    data = response.json()
    return {
        "name": data["name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "url": data["html_url"],
        "languages": retrieve_languages(owner, repo),
        "commits_count": retrieve_commits_count(owner, repo),
    }


def main():
    data_dir = Path(__file__).parent / "_data"
    results = defaultdict(lambda: defaultdict(lambda: {}))

    for owner, repo in load_repo_requests(data_dir):
        print(f"{owner}/{repo}")
        results[owner][repo] = retrieve_repo_info(owner, repo)

    with (Path(data_dir) / "repos_info.yaml").open("w") as stream:
        serialized = yaml.dump(
            {k: dict(v) for k, v in results.items()}, stream, Dumper=Dumper
        )


if __name__ == "__main__":
    main()
