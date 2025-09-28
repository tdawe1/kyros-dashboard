#!/usr/bin/env python3
import os
import requests
try:
    from .base_jsonrpc import JSONRPCServer
    from .env import load_dotenvs
except ImportError:
    # Fallback for when running as console script
    from base_jsonrpc import JSONRPCServer
    from env import load_dotenvs

load_dotenvs()

srv = JSONRPCServer()


@srv.method("coderabbit.request_review")
def request_review(params):
    pr = params.get("pr")
    return {
        "review_id": f"CR-{pr}-001",
        "url": f"https://github.com/org/repo/pull/{pr}#coderabbit",
    }


@srv.method("coderabbit.fetch_feedback")
def fetch_feedback(params):
    owner = params.get("owner")
    repo = params.get("repo")
    pr = params.get("pr")
    if not (owner and repo and pr):
        raise ValueError("owner, repo, pr required")
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    base = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr}"
    reviews = requests.get(base + "/reviews", headers=headers, timeout=30)
    reviews.raise_for_status()
    comments = requests.get(base + "/comments", headers=headers, timeout=30)
    comments.raise_for_status()
    issues_comments = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{pr}/comments",
        headers=headers,
        timeout=30,
    )
    issues_comments.raise_for_status()
    feedback = []
    for r in reviews.json():
        if r.get("state") == "CHANGES_REQUESTED":
            feedback.append(
                {
                    "type": "review",
                    "author": r.get("user", {}).get("login"),
                    "state": r.get("state"),
                    "body": r.get("body"),
                }
            )
    for c in comments.json():
        feedback.append(
            {
                "type": "diff_comment",
                "file": c.get("path"),
                "line": c.get("line"),
                "author": c.get("user", {}).get("login"),
                "body": c.get("body"),
            }
        )
    for ic in issues_comments.json():
        feedback.append(
            {
                "type": "issue_comment",
                "author": ic.get("user", {}).get("login"),
                "body": ic.get("body"),
            }
        )
    return {"owner": owner, "repo": repo, "pr": pr, "suggestions": feedback}


def main():
    srv.serve()


if __name__ == "__main__":
    main()
