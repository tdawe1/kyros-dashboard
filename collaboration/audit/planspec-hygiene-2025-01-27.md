# PlanSpec Hygiene - 2025-01-27

## Changes Made

- **Split T-000 stub**: Moved the T-000 "Add /ready:UP badge" stub from `collaboration/plans/inbox/planspec.yml` to `collaboration/plans/archive/t-000-ready-badge-stub.yml`
- **Single coherent document**: The main planspec.yml now contains only the `2025-09-04-stabilize-develop-release` plan with a single `plan_id` block

## Rationale

The original planspec.yml contained two separate `plan_id` blocks, which violates YAML structure and makes parsing ambiguous. By separating the T-000 stub into its own archived file, we ensure:

1. Clean YAML structure with single `plan_id` per file
2. Clear separation between active plans and archived stubs
3. Easier parsing and validation of plan specifications

## Files Affected

- `collaboration/plans/inbox/planspec.yml` - cleaned up, single plan
- `collaboration/plans/archive/t-000-ready-badge-stub.yml` - new archived stub