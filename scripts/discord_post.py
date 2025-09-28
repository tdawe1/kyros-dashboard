#!/usr/bin/env python3
"""
Post a text/markdown file to a Discord channel via webhook, with optional
header title and links.

Usage:
  DISCORD_WEBHOOK_URL=... python scripts/discord_post.py <file> \
    [--title "Roadmap Updated"] \
    [--project-url URL] [--dashboard-url URL] [--repo-url URL]

Notes:
  - Keeps it simple: sends content as a single message if < 1800 chars,
    otherwise splits into chunks with code fences for readability.
  - You can override the webhook per-call by setting DISCORD_WEBHOOK_URL in env.
"""

import os
import sys
import argparse
import requests


def chunks(s: str, n: int):
    for i in range(0, len(s), n):
        yield s[i : i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--title")
    ap.add_argument("--project-url")
    ap.add_argument("--dashboard-url")
    ap.add_argument("--repo-url")
    args = ap.parse_args()

    hook = os.getenv("DISCORD_WEBHOOK_URL")
    if not hook:
        print("Error: DISCORD_WEBHOOK_URL not set", file=sys.stderr)
        sys.exit(1)

    text = open(args.file, "r", encoding="utf-8").read()

    header_lines = []
    if args.title:
        header_lines.append(f"**{args.title}**")
    link_bits = []
    if args.project_url:
        link_bits.append(f"[GitHub Project]({args.project_url})")
    if args.dashboard_url:
        link_bits.append(f"[Dashboard]({args.dashboard_url})")
    if args.repo_url:
        link_bits.append(f"[Repo]({args.repo_url})")
    if link_bits:
        header_lines.append(" • ".join(link_bits))
    header = "\n".join(header_lines).strip()

    # Discord limit per message ~2000; keep margin for code fences and header
    body = text
    blocks = list(chunks(body, 1800)) if len(body) > 1800 else [body]
    for i, part in enumerate(blocks):
        content_parts = []
        if i == 0 and header:
            content_parts.append(header)
        content_parts.append(f"```\n{part}\n```")
        payload = {"content": "\n".join(content_parts)}
        r = requests.post(hook, json=payload, timeout=15)
        r.raise_for_status()
    print("Posted to Discord")


if __name__ == "__main__":
    main()
