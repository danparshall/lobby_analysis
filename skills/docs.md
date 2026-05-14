# Noridoc: skills

Path: @/skills

### Overview
This folder contains repository-local Nori skills plus a small number of helper scripts used by those skills. The skills define workflow instructions for research sessions, documentation, testing, debugging, branch finishing, and project maintenance.

### How it fits into the larger codebase

@/CLAUDE.md points agents to this folder whenever a workflow-specific task is underway. Most skill folders are instruction-only, but a few include Python helpers that audit docs, paper summaries, or git worktrees. Those helpers operate on repository structure and documentation artifacts rather than on the main @/src packages.

### Core Implementation

Each skill folder uses a `SKILL.md` file to define when and how to run the workflow, and most include a `nori.json` manifest for Nori packaging. Script-backed skills place the helper beside the skill instructions so the workflow and implementation stay together. The scripts use standard library file and git inspection to report repository state to the agent running the skill.

### Things to Know

Skill scripts are maintenance utilities for agent workflows, not production data-pipeline modules. They should preserve user changes and surface discrepancies rather than silently rewriting broad parts of the repo. The instructions in the skill markdown files are the controlling behavior; the Python helpers support those instructions.

Created and maintained by Nori.
