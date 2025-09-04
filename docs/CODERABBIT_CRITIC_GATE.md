# CodeRabbit Critic Gate

This document describes the CodeRabbit Critic Gate implementation that enforces code quality standards by checking for unresolved action-required findings from CodeRabbit feedback.

## Overview

The CodeRabbit Critic Gate is a GitHub Actions workflow that:

1. **Fetches CodeRabbit feedback** on PR open/sync events
2. **Checks for unresolved 'action-required' findings** from CodeRabbit
3. **Fails CI** if unresolved findings exist
4. **Allows bypass** with `critics:ignored` label

## How It Works

### 1. Trigger Events

The gate runs on:
- `pull_request.opened` - When a PR is created
- `pull_request.synchronize` - When a PR is updated with new commits
- `pull_request.reopened` - When a PR is reopened

### 2. Feedback Detection

The gate searches for CodeRabbit feedback in:
- **PR Reviews** - Reviews from `coderabbit[bot]` with `CHANGES_REQUESTED` state
- **Review Comments** - Line-by-line comments from `coderabbit[bot]`
- **Issue Comments** - General PR comments from `coderabbit[bot]`

### 3. Action-Required Detection

The gate looks for the following patterns in CodeRabbit feedback:
- `action-required` (case-insensitive)
- `action required` (case-insensitive)

### 4. Bypass Mechanism

To bypass the gate, add the `critics:ignored` label to the PR. This should only be used for:
- False positives
- Findings that are not applicable to the current context
- Emergency situations where the finding cannot be addressed immediately

## Configuration

### Required Secrets

The gate requires the following GitHub secret:
- `GITHUB_TOKEN` - GitHub personal access token with repo access

### Branch Protection

The gate is included in the branch protection rules in `branch-protection-with-checks.json`:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Collab Guard",
      "CodeRabbit Critic Gate",
      "backend-tests",
      "frontend-tests",
      "e2e-tests",
      "security-scan",
      "build-verification",
      "pr-checks-summary"
    ]
  }
}
```

## Usage

### Normal Operation

1. Create a PR targeting `develop` or `main`
2. CodeRabbit will automatically review the code
3. If CodeRabbit finds issues requiring action, it will comment with "action-required"
4. The gate will detect these findings and fail the CI
5. Address the CodeRabbit feedback and push new commits
6. The gate will re-run and pass once all findings are resolved

### Bypassing the Gate

If you need to bypass the gate:

1. Add the `critics:ignored` label to your PR
2. The gate will skip execution and show a bypass message
3. **Use this sparingly** - only for legitimate cases

### Testing

Run the test script to validate the implementation:

```bash
# Test basic configuration
python scripts/test-coderabbit-gate.py

# Test with a specific PR
python scripts/test-coderabbit-gate.py --pr 123 --owner thomas --repo kyros-dashboard
```

## Troubleshooting

### Common Issues

1. **Gate not running**
   - Check that the workflow file exists at `.github/workflows/coderabbit-critic-gate.yml`
   - Verify the PR is targeting `develop` or `main`
   - Ensure the PR is not in draft mode

2. **False positives**
   - Check if CodeRabbit feedback actually contains "action-required"
   - Verify the feedback is from `coderabbit[bot]` user
   - Consider using the `critics:ignored` label if appropriate

3. **Gate not detecting findings**
   - Ensure CodeRabbit is properly configured in your repository
   - Check that CodeRabbit is actually commenting on the PR
   - Verify the feedback contains the expected keywords

### Debug Information

The gate provides detailed output including:
- Number of action-required findings found
- URLs to each finding
- File and line information (for review comments)
- Bypass status

## Integration with Existing Workflows

The CodeRabbit Critic Gate integrates with:

- **Collab Guard** - Enforces PR base branch and size limits
- **Test Workflows** - Runs alongside backend, frontend, and e2e tests
- **Quality Checks** - Complements security and linting checks
- **Branch Protection** - Prevents merging until all checks pass

## Best Practices

1. **Address findings promptly** - Don't let action-required findings accumulate
2. **Use bypass sparingly** - Only when findings are truly not applicable
3. **Monitor gate performance** - Check for false positives or missed findings
4. **Keep CodeRabbit updated** - Ensure you're using the latest version for best results

## Future Enhancements

Potential improvements to consider:

1. **Configurable keywords** - Allow customizing the action-required detection patterns
2. **Severity levels** - Different handling for different types of findings
3. **Time-based bypass** - Automatic bypass after a certain time period
4. **Integration with other tools** - Support for additional code review tools
5. **Metrics and reporting** - Track gate performance and effectiveness
