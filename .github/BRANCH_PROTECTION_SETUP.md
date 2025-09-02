# Branch Protection Setup Guide

This guide will help you configure GitHub branch protection rules to require tests and code review before merging to the main branch.

## 🔧 Manual Setup Steps

### 1. Navigate to Repository Settings

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar

### 2. Add Branch Protection Rule

1. Click **Add rule** or **Add branch protection rule**
2. In the **Branch name pattern** field, enter: `main`

### 3. Configure Protection Settings

Enable the following settings:

#### ✅ Required Settings

- **☑️ Require a pull request before merging**
  - **☑️ Require approvals**: Set to `1` (or more if you have multiple reviewers)
  - **☑️ Dismiss stale PR approvals when new commits are pushed**
  - **☑️ Require review from code owners** (if you have a CODEOWNERS file)

- **☑️ Require status checks to pass before merging**
  - **☑️ Require branches to be up to date before merging**
  - In the search box, add these required status checks:
    - `Backend Tests`
    - `Frontend Tests`
    - `E2E Tests`
    - `Security Scan`
    - `Build Verification`
    - `PR Checks Summary`

- **☑️ Require conversation resolution before merging**

- **☑️ Require signed commits** (optional but recommended)

- **☑️ Require linear history** (optional but recommended)

#### ⚠️ Additional Settings (Optional)

- **☑️ Restrict pushes that create files larger than 100 MB**
- **☑️ Require deployments to succeed before merging** (if you want staging deployments to pass)

### 4. Save the Rule

Click **Create** to save the branch protection rule.

## 🔍 Verification

After setting up branch protection:

1. Create a test branch: `git checkout -b test-branch-protection`
2. Make a small change and commit
3. Push the branch: `git push origin test-branch-protection`
4. Create a pull request to main
5. Verify that:
   - You cannot merge without approval
   - All status checks must pass
   - The PR shows "Required" status for all checks

## 📋 Required Status Checks

The following status checks must pass before merging:

| Check Name | Description |
|------------|-------------|
| `Backend Tests` | Python unit tests, linting, and formatting |
| `Frontend Tests` | JavaScript/React unit tests and linting |
| `E2E Tests` | End-to-end tests with Playwright |
| `Security Scan` | Security vulnerability scanning |
| `Build Verification` | Ensures both frontend and backend build successfully |
| `PR Checks Summary` | Overall summary of all checks |

## 🚨 Troubleshooting

### If status checks don't appear:

1. Make sure the workflow files are in the `.github/workflows/` directory
2. Check that the job names in the workflow match the required status check names
3. Ensure the workflows are triggered on pull requests
4. Wait a few minutes for GitHub to recognize the new workflows

### If you can't merge after all checks pass:

1. Verify that all required status checks are listed in the branch protection settings
2. Check that the PR has the required number of approvals
3. Ensure all conversations are resolved
4. Make sure the branch is up to date with main

## 🔄 Workflow

With branch protection enabled, your workflow will be:

1. **Create feature branch** from main
2. **Make changes** and commit frequently [[memory:7940605]]
3. **Push to feature branch** (triggers PR checks)
4. **Create pull request** to main
5. **Wait for all checks to pass** (automated)
6. **Request code review** from team members
7. **Address review feedback** if needed
8. **Merge after approval** and all checks pass

## 📝 Code Review Guidelines

### For Reviewers:
- Check code quality and logic
- Verify tests cover new functionality
- Ensure security best practices
- Review documentation updates
- Test the changes if possible

### For Authors:
- Write clear commit messages
- Include tests for new features
- Update documentation as needed
- Respond to review feedback promptly
- Keep PRs focused and reasonably sized

## 🎯 Benefits

This setup provides:

- **Quality Assurance**: All code is tested before merging
- **Security**: Automated security scanning
- **Code Review**: Human oversight of all changes
- **Consistency**: Enforced coding standards
- **Reliability**: Reduced risk of breaking changes in production
- **Collaboration**: Clear process for team contributions

## 🔧 Advanced Configuration

### CODEOWNERS File

Create a `.github/CODEOWNERS` file to automatically request reviews from specific team members:

```
# Global owners
* @username1 @username2

# Backend code
/backend/ @backend-team

# Frontend code
/frontend/ @frontend-team

# Documentation
/docs/ @docs-team
```

### Custom Status Checks

You can add additional required status checks by:

1. Creating new jobs in the workflow files
2. Adding the job names to the branch protection settings
3. Ensuring the jobs run on pull requests

### Staging Environment

Consider setting up a staging environment that deploys from the `develop` branch for additional testing before merging to main.
