#!/bin/bash

# Add Required Status Checks Script
# Run this after creating your first PR to add the required status checks

set -e

echo "🔍 Adding Required Status Checks to Branch Protection"
echo "====================================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📁 Repository: $REPO"

echo ""
echo "🔧 Adding required status checks to branch protection..."

# Update branch protection with status checks
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --input branch-protection-with-checks.json

echo "✅ Required status checks added successfully!"

echo ""
echo "🔍 Required status checks now configured:"
echo "  • Backend Tests"
echo "  • Frontend Tests"
echo "  • E2E Tests"
echo "  • Security Scan"
echo "  • Build Verification"
echo "  • PR Checks Summary"

echo ""
echo "📋 Complete protection rules:"
echo "  • Require pull request reviews before merging"
echo "  • Require status checks to pass before merging"
echo "  • Require branches to be up to date before merging"
echo "  • Require review from code owners"
echo "  • Dismiss stale PR approvals when new commits are pushed"
echo "  • Block force pushes"
echo "  • Block branch deletion"

echo ""
echo "🎉 Branch protection is now fully configured!"
echo "All future PRs will require these checks to pass before merging."
