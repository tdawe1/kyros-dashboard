#!/usr/bin/env python3
import os
import requests
from mcp.base_jsonrpc import JSONRPCServer
from mcp.env import load_dotenvs

load_dotenvs()

srv = JSONRPCServer()


@srv.method("vercel.get_deployment")
def get_deployment(params):
    dep = params.get("deployment_id")
    token = os.getenv("VERCEL_TOKEN")
    if not token:
        return {"deployment_id": dep, "state": "UNKNOWN", "stub": True}
    url = f"https://api.vercel.com/v13/deployments/{dep}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return {"deployment_id": dep, "state": data.get("state"), "url": data.get("url")}


def main():
    srv.serve()


if __name__ == "__main__":
    main()
