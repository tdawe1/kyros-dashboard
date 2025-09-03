#!/usr/bin/env python3
import os
import requests
from mcp.base_jsonrpc import JSONRPCServer
from mcp.env import load_dotenvs

load_dotenvs()

srv = JSONRPCServer()


@srv.method("railway.capabilities")
def capabilities(params):
    ok = bool(os.getenv("RAILWAY_TOKEN"))
    return {"configured": ok, "endpoints": ["get_deployment"]}


@srv.method("railway.get_deployment")
def get_deployment(params):
    dep_id = params.get("deployment_id")
    if not dep_id:
        raise ValueError("deployment_id is required")
    token = os.getenv("RAILWAY_TOKEN")
    if not token:
        return {"deployment_id": dep_id, "status": "UNKNOWN", "stub": True}
    url = "https://backboard.railway.app/graphql"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    query = """
      query Deployment($id: String!) { deployment(id: $id) { id status url createdAt } }
    """
    variables = {"id": dep_id}
    resp = requests.post(
        url, headers=headers, json={"query": query, "variables": variables}, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    dep = data.get("data", {}).get("deployment")
    if not dep:
        raise RuntimeError(f"Railway response error: {data}")
    return {
        "deployment_id": dep.get("id"),
        "status": dep.get("status"),
        "url": dep.get("url"),
    }


def main():
    srv.serve()


if __name__ == "__main__":
    main()
