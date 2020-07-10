#! /bin/env python3
from pathlib import Path
from collections import defaultdict
import yaml
import requests


def load_repo_requests(data_dir):
    with (data_dir / "repos.yaml").open() as file:
        repos = yaml.load(file, yaml.CLoader)
    return ((r["owner"], r["repo"]) for r in repos)


def retrieve_repo_info(owner, repo):
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
    if response.status_code != 200:
        raise RuntimeError("Repository does not exist: " + response.content)

    data = response.json()
    return {
        "name": data["name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "url": data["html_url"]
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
