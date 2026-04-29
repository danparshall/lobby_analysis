# Research Log: statute-retrieval
Created: 2026-04-29
Purpose: Build a scalable two-pass statute retrieval pipeline (retrieval agent → scoring agent) that can run annually on all 50 states without manual per-state URL curation

## Conversations

(newest first)

- **20260429_retrieval_pipeline_design** — Cleaned up merged worktrees/branches, re-pulled Justia statute data for new 3-state calibration subset (CA/TX/OH), designed two-pass retrieval architecture (LLM-driven cross-reference discovery, 2-hop limit, enriched manifests, PRI 2010 as test suite)

## Plans

(newest first)

- **20260429_two_pass_retrieval_agent** — Two-pass pipeline: retrieval agent follows cross-references (2-hop, LLM-driven), enriched manifests, PRI 2010 as test suite. OH first. Originated from `convos/20260429_retrieval_pipeline_design.md`.
