"""
Core package init kept lightweight on purpose.

Avoid importing heavy submodules at package import time to prevent optional
dependencies (like the OpenAI SDK) from blocking unrelated imports. Modules
should import the specific `core.*` subpackages they need directly.
"""

# Intentionally no eager imports here.
