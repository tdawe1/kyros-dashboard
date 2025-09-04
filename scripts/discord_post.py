#!/usr/bin/env python3
"""
Post a text/markdown file to a Discord channel via webhook.

Usage:
  DISCORD_WEBHOOK_URL=... python scripts/discord_post.py ROADMAP.md

Notes:
  - Keeps it simple: sends content as a single message if < 1800 chars,
    otherwise splits into chunks with code fences for readability.
"""

import os
import sys
import textwrap
import requests


def chunks(s: str, n: int):
    for i in range(0, len(s), n):
        yield s[i : i + n]


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/discord_post.py <file>", file=sys.stderr)
        sys.exit(1)
    hook = os.getenv("DISCORD_WEBHOOK_URL")
    if not hook:
        print("Error: DISCORD_WEBHOOK_URL not set", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    text = open(path, "r", encoding="utf-8").read()
    # Discord limit per message ~2000; keep margin for code fences
    if len(text) <= 1800:
        payload = {"content": f"```\n{text}\n```"}
        r = requests.post(hook, json=payload, timeout=15)
        r.raise_for_status()
    else:
        for part in chunks(text, 1800):
            payload = {"content": f"```\n{part}\n```"}
            r = requests.post(hook, json=payload, timeout=15)
            r.raise_for_status()
    print("Posted to Discord")


if __name__ == "__main__":
    main()

