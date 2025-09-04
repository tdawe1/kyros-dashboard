#!/usr/bin/env python3
"""
Validate CodeRabbit Critic Gate implementation without requiring GitHub API access.

This script validates the configuration and structure of the CodeRabbit critic gate
without making external API calls.

Usage:
  python scripts/validate-coderabbit-gate.py
"""

import json
import sys
from pathlib import Path


def validate_workflow_file():
    """Validate the CodeRabbit critic gate workflow file."""
    workflow_path = Path(".github/workflows/coderabbit-critic-gate.yml")
    
    if not workflow_path.exists():
        print("❌ CodeRabbit critic gate workflow file not found")
        return False
    
    print("✅ CodeRabbit critic gate workflow file exists")
    
    # Read and validate content
    content = workflow_path.read_text()
    
    # Check for required components
    required_components = [
        "CodeRabbit Critic Gate",
        "critics:ignored",
        "action-required",
        "coderabbit[bot]",
        "GITHUB_TOKEN",
        "pull_request:",
        "pull_request_target:",
        "jobs:",
        "coderabbit-critic-gate:"
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Workflow file missing required components: {missing_components}")
        return False
    
    print("✅ Workflow file contains all required components")
    
    # Check for proper YAML structure (basic validation)
    try:
        import yaml
        yaml.safe_load(content)
        print("✅ Workflow file has valid YAML syntax")
    except ImportError:
        print("⚠️  PyYAML not available - skipping YAML syntax check")
    except Exception as e:
        print(f"❌ Workflow file has invalid YAML syntax: {e}")
        return False
    
    return True


def validate_branch_protection():
    """Validate branch protection configuration."""
    protection_path = Path("branch-protection-with-checks.json")
    
    if not protection_path.exists():
        print("❌ Branch protection configuration file not found")
        return False
    
    try:
        with open(protection_path) as f:
            config = json.load(f)
        
        # Check structure
        if "required_status_checks" not in config:
            print("❌ Branch protection missing required_status_checks section")
            return False
        
        if "contexts" not in config["required_status_checks"]:
            print("❌ Branch protection missing contexts array")
            return False
        
        contexts = config["required_status_checks"]["contexts"]
        
        if "CodeRabbit Critic Gate" not in contexts:
            print("❌ CodeRabbit Critic Gate not found in branch protection contexts")
            return False
        
        print("✅ CodeRabbit Critic Gate found in branch protection contexts")
        
        # Check that it's in a reasonable position (after Collab Guard)
        collab_guard_index = contexts.index("Collab Guard") if "Collab Guard" in contexts else -1
        coderabbit_index = contexts.index("CodeRabbit Critic Gate")
        
        if collab_guard_index >= 0 and coderabbit_index < collab_guard_index:
            print("⚠️  CodeRabbit Critic Gate should come after Collab Guard in the contexts list")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to parse branch protection configuration: {e}")
        return False


def validate_documentation():
    """Validate that documentation exists and is complete."""
    doc_path = Path("docs/CODERABBIT_CRITIC_GATE.md")
    
    if not doc_path.exists():
        print("❌ CodeRabbit Critic Gate documentation not found")
        return False
    
    print("✅ CodeRabbit Critic Gate documentation exists")
    
    # Check for key sections
    content = doc_path.read_text()
    required_sections = [
        "# CodeRabbit Critic Gate",
        "## Overview",
        "## How It Works",
        "## Configuration",
        "## Usage",
        "## Troubleshooting"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Documentation missing required sections: {missing_sections}")
        return False
    
    print("✅ Documentation contains all required sections")
    return True


def validate_acceptance_criteria():
    """Validate that all acceptance criteria are met."""
    print("\n🔍 Validating Acceptance Criteria:")
    
    criteria = [
        ("CodeRabbit feedback imported on PR open/sync", "pull_request:" in Path(".github/workflows/coderabbit-critic-gate.yml").read_text()),
        ("CI fails if unresolved 'action-required' findings exist", "action-required" in Path(".github/workflows/coderabbit-critic-gate.yml").read_text()),
        ("Gate bypassable with 'critics:ignored' label", "critics:ignored" in Path(".github/workflows/coderabbit-critic-gate.yml").read_text()),
        ("Gate documented", Path("docs/CODERABBIT_CRITIC_GATE.md").exists()),
    ]
    
    all_passed = True
    for criterion, passed in criteria:
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    print("🔍 Validating CodeRabbit Critic Gate Implementation")
    print("=" * 60)
    
    tests = [
        ("Workflow File", validate_workflow_file),
        ("Branch Protection", validate_branch_protection),
        ("Documentation", validate_documentation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    # Validate acceptance criteria
    print(f"\n🧪 Testing Acceptance Criteria...")
    if validate_acceptance_criteria():
        passed += 1
        total += 1
    else:
        print("❌ Acceptance criteria validation failed")
        total += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All validations passed! CodeRabbit Critic Gate is ready.")
        print("\n📋 Next Steps:")
        print("1. Ensure GITHUB_TOKEN is set in repository secrets")
        print("2. Test with a real PR that has CodeRabbit feedback")
        print("3. Verify the gate works as expected in practice")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
