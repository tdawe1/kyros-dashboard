#!/usr/bin/env python3
"""
Test script for CodeRabbit Critic Gate implementation.

This script validates that the CodeRabbit critic gate workflow is properly configured
and can detect action-required findings from CodeRabbit feedback.

Usage:
  python scripts/test-coderabbit-gate.py [--pr PR_NUMBER] [--owner OWNER] [--repo REPO]
"""

import argparse
import json
import os
import requests
import sys
from pathlib import Path


def test_github_api_access():
    """Test if we can access GitHub API with the provided token."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        response.raise_for_status()
        user_data = response.json()
        print(f"✅ GitHub API access successful - authenticated as {user_data.get('login', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ GitHub API access failed: {e}")
        return False


def test_workflow_file():
    """Test if the CodeRabbit critic gate workflow file exists and is valid."""
    workflow_path = Path(".github/workflows/coderabbit-critic-gate.yml")
    
    if not workflow_path.exists():
        print("❌ CodeRabbit critic gate workflow file not found")
        return False
    
    print("✅ CodeRabbit critic gate workflow file exists")
    
    # Basic validation - check for key components
    content = workflow_path.read_text()
    required_components = [
        "CodeRabbit Critic Gate",
        "critics:ignored",
        "action-required",
        "coderabbit[bot]",
        "GITHUB_TOKEN"
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Workflow file missing required components: {missing_components}")
        return False
    
    print("✅ Workflow file contains all required components")
    return True


def test_branch_protection():
    """Test if branch protection rules include the CodeRabbit critic gate."""
    protection_path = Path("branch-protection-with-checks.json")
    
    if not protection_path.exists():
        print("❌ Branch protection configuration file not found")
        return False
    
    try:
        with open(protection_path) as f:
            config = json.load(f)
        
        contexts = config.get("required_status_checks", {}).get("contexts", [])
        
        if "CodeRabbit Critic Gate" not in contexts:
            print("❌ CodeRabbit Critic Gate not found in branch protection contexts")
            return False
        
        print("✅ CodeRabbit Critic Gate found in branch protection contexts")
        return True
    except Exception as e:
        print(f"❌ Failed to parse branch protection configuration: {e}")
        return False


def test_pr_feedback(owner, repo, pr_number):
    """Test fetching CodeRabbit feedback from a specific PR."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        # Fetch PR reviews
        reviews_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        reviews_response = requests.get(reviews_url, headers=headers, timeout=30)
        reviews_response.raise_for_status()
        reviews = reviews_response.json()
        
        # Fetch PR review comments
        comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        comments_response = requests.get(comments_url, headers=headers, timeout=30)
        comments_response.raise_for_status()
        comments = comments_response.json()
        
        # Check for CodeRabbit feedback
        coderabbit_feedback = []
        
        for review in reviews:
            if review.get("user", {}).get("login") == "coderabbit[bot]":
                coderabbit_feedback.append({
                    "type": "review",
                    "state": review.get("state"),
                    "body": review.get("body", "")[:100] + "..." if len(review.get("body", "")) > 100 else review.get("body", "")
                })
        
        for comment in comments:
            if comment.get("user", {}).get("login") == "coderabbit[bot]":
                coderabbit_feedback.append({
                    "type": "comment",
                    "file": comment.get("path"),
                    "line": comment.get("line"),
                    "body": comment.get("body", "")[:100] + "..." if len(comment.get("body", "")) > 100 else comment.get("body", "")
                })
        
        print(f"✅ Found {len(coderabbit_feedback)} CodeRabbit feedback items in PR #{pr_number}")
        
        if coderabbit_feedback:
            print("CodeRabbit feedback found:")
            for i, feedback in enumerate(coderabbit_feedback, 1):
                print(f"  {i}. {feedback['type']}: {feedback['body']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch PR feedback: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test CodeRabbit Critic Gate implementation")
    parser.add_argument("--pr", type=int, help="PR number to test with")
    parser.add_argument("--owner", default="thomas", help="Repository owner")
    parser.add_argument("--repo", default="kyros-dashboard", help="Repository name")
    
    args = parser.parse_args()
    
    print("🔍 Testing CodeRabbit Critic Gate Implementation")
    print("=" * 50)
    
    tests = [
        ("GitHub API Access", test_github_api_access),
        ("Workflow File", test_workflow_file),
        ("Branch Protection", test_branch_protection),
    ]
    
    if args.pr:
        tests.append(("PR Feedback Fetch", lambda: test_pr_feedback(args.owner, args.repo, args.pr)))
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! CodeRabbit Critic Gate is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
