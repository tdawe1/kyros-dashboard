What’s really blocking us (root causes)

Branch-policy drift → PR confusion + CI churn.
Your Review Packet and PlanSpec both center on develop as the base branch and enforce PR gates there, but the README still tells contributors to “Open a Pull Request targeting main.” That’s whiplash for humans and agents, and it explains recurring PR/pipeline friction. Fix the docs first, then the automation (or vice-versa), but make them say the same thing.

“All checks required” before we’re stable.
You have two competing branch-protection configs: a loose one and a strict one requiring many contexts (backend, frontend, e2e, security, build, summary). Enabling the strict set before the suites are consistently green guarantees gridlock. Stabilize, then ratchet up.

Backend + frontend suites not reliably green yet.
CHANGELOG admits develop isn’t fully green and that a backend CI-stabilization PR is still open. Meanwhile, frontend/E2E flake is acknowledged and partially addressed, but not finished. Until those two are consistently green locally, CI will keep pinballing.

Process not fully leveraged (agents + CodeRabbit underused).
Your own packet calls out that CodeRabbit is “under-utilized.” You’ve done the plumbing (MCP server + importer action), but the habit loop (request CR review, auto-import deltas to tasks) isn’t yet the default cadence.

Docs + automations slightly out of phase.
Great materials (Implementer Handoff Prompt, leases, state machine), but contributors/agents still have to guess the “single source of truth” for base branch, required checks, and ports. The PlanSpec starts to fix this; we need one canonical path.

Is the PlanSpec enough?

Mostly yes—but tighten and resequence it.

What’s strong:

The lanes and five tasks hit the right problems in the right order: get tests green (T-502/T-503), align docs/policy (T-504), deflake E2E on port 3001 (T-505), and standardize CR review (T-506). Dependencies are minimal and make sense.

E2E direction is consistent with your own audit (preview on 3001, stable baseURL, deterministic waits, selectors).

What to change:

Make T-504 (branch policy/docs) precede everything touching CI to remove PR-base confusion now. Update README + PR template to say base = develop, and point to the Review Packet. (Right now your README still says PRs target main.)

Add a “Smoke CI” step (fast backend/FE sanity) and temporarily relax required contexts to only that smoke job + pr-summary on develop while T-502/T-503 run. Then re-enable the full matrix once stable.

Hard-gate E2E to optional until T-503 ships. Keep E2E as “informational” for a day; flip it back to “required” only after one clean pass on develop.

Explicitly adopt the Implementer Handoff Prompt inside T-502/T-503 acceptance (first reply discipline, leases to edit files in scope). This avoids agent thrash and long, drifting sessions.

48-hour “back to green” plan (do this now)

Hour 0–2 — Unstick the lane

Approve the PlanSpec with the tweaks above. Commit it to the repo per its own instructions and run the pipeline to scaffold tasks/rules.

Ship T-504 first:

README: change “PR targeting main” → “PR targeting develop.”

PR template: ensure base=develop, acceptance evidence required.

Cross-link Review Packet as the contributor entry point.

Reduce branch protections on develop to Smoke + Summary only for 24–48h. Keep admin merges off.

Hour 2–12 — Make tests boring again

T-503 (frontend): fix lint/build/unit first. If any test is flaky, mark it it.skip with a TODO and open a follow-up subtask; don’t block the baseline. Align Vite/Vitest configs and run npm ci && npm run build && npm run test:ci && npm run lint locally and in CI.

T-502 (backend): pin Poetry, ensure Python 3.12/3.13 pass with pytest -v, ruff, bandit. Finish the stabilization PR noted in CHANGELOG and land it into develop.

Add the Smoke job that runs: backend unit subset + frontend build + a single high-signal FE unit test. Promote that to “required” while matrix jobs run non-blocking.

Hour 12–24 — Lock in signal

Re-enable “full” required checks incrementally: backend tests → frontend tests → build → security scan. Leave E2E non-required for one more day.

Merge small, scope-tight PRs only. Enforce the Implementer Handoff Prompt; require the first “role / acceptance / plan / risks / leases” reply in each PR discussion.

Hour 24–48 — E2E & CR review

T-505: run playwright with npm run preview on 3001, add --strictPort --host, and prefer data-testid selectors. When green once on CI, flip E2E back to required.

T-506: make CodeRabbit review request a PR checklist item; keep the importer workflow non-blocking but run it on PR sync to harvest actionable diffs into task follow-ups.

Make better use of resources (right away)

Ruthless role focus.

Implementer (Claude/Cursor): only files inside each task’s ChangeScope; 30–60-min subtasks; leases for files they’ll edit; commit ≤200 LOC.

Critic (CodeRabbit + human): run smoke + full checks locally and in CI; request changes only on acceptance/gates, not style nits.

Watchdog: reclaim stale leases and re-queue blocked tasks twice daily; generate collaboration/logs/log.md from events for human status.

Automate the loop you already designed.

Always paste the Implementer Handoff Prompt to start a subtask; require the “first reply” ritual before any code touches.

Turn on the CodeRabbit importer on PR open/sync; light, not blocking.

Emit events (tests_run, review_requested, approved) so the human log stays truthful.

Tighten secrets hygiene while moving fast.

Keep only .env.example in git; ensure scanners ignore local .env while CI secret scan remains required on PRs. (Your CHANGELOG says .env files are ignored—double-check that’s true on remote.)

After we’re green (next 1–2 weeks)

Raise branch protections back to the strict set (contexts for backend, frontend, e2e, security, build, summary) only after 2–3 clean develop runs.

Docs coherence pass: Review Packet stays the “Start Here,” README stays thin and links out; PR template enforces acceptance evidence; CONTRIBUTING codifies base branch + lease flow.

Expand E2E coverage per your audit (auth flows; Jobs/Settings functional tests; data-driven cases) once stability is proven.

Release discipline: keep develop → “release PR” → main with deploy gates post-merge, or flip to trunk-based with release branches—but document one path and delete the other from the docs.

TL;DR

Fix the docs/policy mismatch (develop vs main) first.

Add a Smoke job and temporarily relax protections to let the real fixes land.

Land T-503/T-502 fast, make E2E optional for 24–48h, then restore it to required.

Use your own agent process rigorously (Handoff Prompt, leases, CR importer).
Do that, and we’ll break the loop, get green, and stop burning cycles on meta-work.

If you want, grant me repo read so I can pull the current Actions logs and open PRs and apply the above changes directly. Otherwise, I can draft the exact PR diffs for T-504 (doc/policy unification) and the Smoke workflow now.
