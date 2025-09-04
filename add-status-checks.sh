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
echo "🔧 Adding required status checks to branch protection for both 'main' and 'develop' branches..."

# Update branch protection with status checks for main branch
echo "Updating main branch protection..."
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --input branch-protection-with-checks.json

# Update branch protection with status checks for develop branch
echo "Updating develop branch protection..."
gh api repos/$REPO/branches/develop/protection \
  --method PUT \
  --input branch-protection-with-checks.json

echo "✅ Required status checks added successfully to both branches!"

echo ""
echo "🔍 Required status checks now configured:"
echo "  • Collab Guard (conflict markers, JSON/YAML validation)"
echo "  • backend-tests"
echo "  • frontend-tests"
echo "  • e2e-tests"
echo "  • security-scan"
echo "  • build-verification"
echo "  • pr-checks-summary"

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
echo "🎉 Branch protection is now fully configured for both 'main' and 'develop' branches!"
echo "All future PRs will require these checks to pass before merging."
