#! /bin/env python3
import re
from pathlib import Path
from collections import defaultdict
import yaml
import requests

RE_PAGE_NUMBER = re.compile(r"(?:&|\?)page=(\d+)")


def load_repo_requests(data_dir):
    with (data_dir / "repos.yaml").open() as file:
        repos = yaml.load(file, yaml.CLoader)
    return ((r["owner"], r["repo"]) for r in repos)


def retrieve_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = requests.get(url)
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
    response = requests.get(url)
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
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
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
        results[owner][repo] = retrieve_repo_info(owner, repo)

    with (Path(data_dir) / "repos_info.yaml").open("w") as stream:
        serialized = yaml.dump(
            {k: dict(v) for k, v in results.items()}, stream
        )


if __name__ == "__main__":
    main()
