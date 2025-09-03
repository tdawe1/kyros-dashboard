# LLM Agent Collaboration Workflow

This document outlines the workflow for multiple LLM agents to collaborate on this project. The goal is to ensure coordination, prevent conflicts, and maintain a clear history of work.

## The Collaboration Hub

A central `collaboration` directory serves as the hub for agent coordination. It contains:

- `state.json`: The single source of truth for the project's state, including tasks and file locks.
- `log.md`: A log of agent activities.

## Agent Workflow

1.  **Sync with `state.json`**:
    - Before starting any work, an agent must lock and read `state.json` to get the latest project state. A lock is achieved by creating a `state.json.lock` file.

2.  **Claim a Task**:
    - The agent identifies a `todo` task from the `tasks` list.
    - It claims the task by setting the `status` to `in_progress` and its own ID as the `assignee`.

3.  **Lock Files**:
    - The agent adds entries to the `file_locks` dictionary for all files it intends to modify. This prevents other agents from editing the same files.

4.  **Update State and Unlock**:
    - The agent writes the updated information back to `state.json` and then removes the `state.json.lock` file.

5.  **Execute the Task**:
    - The agent performs the coding task.
    - It logs its progress, decisions, and any significant findings in `log.md`.

6.  **Complete the Task**:
    - Once the task is finished, the agent locks `state.json` again.
    - It updates the task's `status` to `done`.
    - It removes the file locks for the files it edited.
    - It writes the changes to `state.json` and removes the lock.
