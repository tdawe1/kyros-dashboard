#!/bin/bash

# Branch Protection Setup Script for Kyros Dashboard
# This script helps you set up branch protection rules via GitHub CLI

set -e

echo "🛡️  Setting up Branch Protection for Kyros Dashboard"
echo "=================================================="

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

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository."
    exit 1
fi

echo ""
echo "🔧 Setting up branch protection rules for 'main' branch..."

# First, let's set up basic protection without status checks
echo "Setting up basic branch protection..."

gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --input branch-protection.json

echo "✅ Basic branch protection created!"

echo ""
echo "⚠️  Note: Status checks will be added after the first PR is created."
echo "   The status checks need to exist in GitHub before they can be required."
echo "   After creating your first PR, you can add the required status checks manually:"
echo "   - Backend Tests"
echo "   - Frontend Tests"
echo "   - E2E Tests"
echo "   - Security Scan"
echo "   - Build Verification"
echo "   - PR Checks Summary"

echo ""
echo "📋 Summary of protection rules:"
echo "  • Require pull request reviews before merging"
echo "  • Require review from code owners"
echo "  • Dismiss stale PR approvals when new commits are pushed"
echo "  • Block force pushes"
echo "  • Block branch deletion"

echo ""
echo "📝 Next steps:"
echo "  1. Create a test branch: git checkout -b test-branch-protection"
echo "  2. Make a small change and commit"
echo "  3. Push the branch: git push origin test-branch-protection"
echo "  4. Create a pull request to main"
echo "  5. Wait for the PR checks to run (this creates the status checks in GitHub)"
echo "  6. After the first PR, manually add the required status checks in GitHub Settings"
echo "  7. Verify that all checks run and approval is required"

echo ""
echo "🎉 Branch protection setup complete!"
echo "Your main branch is now protected and requires code review before merging."
