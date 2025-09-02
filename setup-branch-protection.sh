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

# Create branch protection rule
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Backend Tests","Frontend Tests","E2E Tests","Security Scan","Build Verification","PR Checks Summary"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

echo "✅ Branch protection rules created successfully!"

echo ""
echo "📋 Summary of protection rules:"
echo "  • Require pull request reviews before merging"
echo "  • Require status checks to pass before merging"
echo "  • Require branches to be up to date before merging"
echo "  • Require review from code owners"
echo "  • Dismiss stale PR approvals when new commits are pushed"
echo "  • Block force pushes"
echo "  • Block branch deletion"

echo ""
echo "🔍 Required status checks:"
echo "  • Backend Tests"
echo "  • Frontend Tests"
echo "  • E2E Tests"
echo "  • Security Scan"
echo "  • Build Verification"
echo "  • PR Checks Summary"

echo ""
echo "📝 Next steps:"
echo "  1. Create a test branch: git checkout -b test-branch-protection"
echo "  2. Make a small change and commit"
echo "  3. Push the branch: git push origin test-branch-protection"
echo "  4. Create a pull request to main"
echo "  5. Verify that all checks run and approval is required"

echo ""
echo "🎉 Branch protection setup complete!"
echo "Your main branch is now protected and requires code review before merging."
