# Generative AI usage log

The report must include an appendix, *Declaration of Generative AI Tool Usage*, that lists the tools used, the key prompts, the scope of each use, and at least one case where the AI output was wrong or suboptimal and how the team fixed it. Log every use here as it happens so the appendix is easy to write later.

| Date | Member | Tool | Prompt (summary) | Scope | What we kept / changed and why |
|------|--------|------|------------------|-------|--------------------------------|
| 2026-11-09 | TODO | Claude Code (Claude Opus 5.5) | "Read Project_Description.pdf and create the skeleton for the assignment (folders, scripts)" | Repository structure and modules, test scaffolding, LaTeX report template | We reviewed the structure and changed it to make it simpler and clearer (see example 2 below) |

## AI output that was incorrect or suboptimal

At least one is required.

### 1. Station codes silently turned into decimals

The AI wrote the function `reindex_daily` in `cleaning.py`, which gives every station one row per calendar day by reindexing its data on a full date range and then filling the station columns (`state_code`, `county_code`, `site_num`, `state`, ...) forward into the new empty days. The code ran without errors, but when we inspected the output parquet we saw that `state_code`, `county_code` and `site_num` were stored as `1.0`, `73.0`, `23.0` instead of integers. We fixed it by casting the three code columns back to `int` at the end of `reindex_daily`.

### 1. Over-complicated project skeleton

When asked for the project skeleton, the AI created more structure than the assignment needed: both a `report/` and a `reports/` folder, an extra `data/interim/` stage, and a `tests/` folder with a test suite. We simplified the structure.
