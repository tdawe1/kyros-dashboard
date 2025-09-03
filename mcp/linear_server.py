#!/usr/bin/env python3
import os
import requests
from mcp.base_jsonrpc import JSONRPCServer
from mcp.env import load_dotenvs

load_dotenvs()

srv = JSONRPCServer()


@srv.method("linear.capabilities")
def capabilities(params):
    ok = bool(os.getenv("LINEAR_API_TOKEN"))
    return {"configured": ok, "endpoints": ["create_issue"]}


@srv.method("linear.create_issue")
def create_issue(params):
    """
    Create a Linear issue via GraphQL.
    Required params: team_id, title; optional: description, label_ids[]
    Env: LINEAR_API_TOKEN
    """
    token = os.getenv("LINEAR_API_TOKEN")
    if not token:
        # Fallback stub when not configured
        return {
            "issue_id": "LIN-123",
            "url": "https://linear.app/example/issue/LIN-123",
            "stub": True,
        }

    team_id = params.get("team_id")
    title = params.get("title")
    description = params.get("description", "")
    label_ids = params.get("label_ids", [])
    if not team_id or not title:
        raise ValueError("team_id and title are required")

    url = "https://api.linear.app/graphql"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    mutation = """
      mutation IssueCreate($input: IssueCreateInput!) {
        issueCreate(input: $input) { success issue { id identifier url } }
      }
    """
    variables = {
        "input": {
            "teamId": team_id,
            "title": title,
            "description": description,
            **({"labelIds": label_ids} if label_ids else {}),
        }
    }
    resp = requests.post(
        url,
        headers=headers,
        json={"query": mutation, "variables": variables},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    issue = data.get("data", {}).get("issueCreate", {}).get("issue")
    if not issue:
        raise RuntimeError(f"Linear error: {data}")
    return {
        "issue_id": issue["identifier"],
        "url": issue.get("url"),
        "id": issue.get("id"),
    }


def main():
    srv.serve()


if __name__ == "__main__":
    main()
