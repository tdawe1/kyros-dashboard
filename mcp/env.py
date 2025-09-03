#!/usr/bin/env python3
"""
Lightweight environment loader for MCP servers.

Behavior:
- If python-dotenv is available, load variables from:
  1) .env (project root)
  2) collaboration/.env
  without overriding already-set env vars.
- Silent no-op if python-dotenv is not installed.
"""

from __future__ import annotations

from pathlib import Path


def load_dotenvs() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        # Not installed or import error: skip silently
        return

    # Do not override variables already present in the environment
    cwd = Path.cwd()
    load_dotenv(cwd / ".env", override=False)
    load_dotenv(cwd / "collaboration" / ".env", override=False)


__all__ = ["load_dotenvs"]
