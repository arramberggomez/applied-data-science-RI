# Generative AI usage log

The report must include an appendix, *Declaration of Generative AI Tool Usage*, that lists the tools used, the key prompts, the scope of each use, and at least one case where the AI output was wrong or suboptimal and how the team fixed it. Log every use here as it happens so the appendix is easy to write later.

| Date | Member | Tool | Prompt (summary) | Scope | What we kept / changed and why |
|------|--------|------|------------------|-------|--------------------------------|
| 2026-11-09 | TODO | Claude Code (Claude Opus 5.5) | "Read Project_Description.pdf and create the skeleton for the assignment (folders, scripts, main functions)" | Repository structure, module and function stubs, CLI, test scaffolding, LaTeX report template | TODO: review the structure critically, e.g. check the Kaggle slug and the AQI column names against the real data |

## AI output that was incorrect or suboptimal

At least one is required.

### 1. Station codes silently turned into decimals (incorrect code)

- **What the AI proposed:** In `cleaning.py`, the function `reindex_daily` gives every station one row per calendar day. It does this by reindexing each station's data on a full date range and then filling the station columns (`state_code`, `county_code`, `site_num`, `state`, ...) forward into the new empty days.
- **How we noticed it was wrong:** The code ran without errors, but inspecting the output parquet showed `state_code`, `county_code` and `site_num` stored as `1.0`, `73.0`, `23.0` instead of integers. Reindexing inserts empty rows (NaN), and pandas cannot store NaN in an integer column, so it silently converts the whole column to float. Filling the gaps afterwards does not convert it back.
- **What we did instead:** We cast the three code columns back to `int` at the end of `reindex_daily`, and checked the dtypes of the saved file. Lesson: code that runs is not necessarily correct; always inspect the output (`df.dtypes`, `df.head()`), not just whether it crashes.

### 2. Over-complicated project skeleton (suboptimal proposal)

- **What the AI proposed:** When asked for the project skeleton, the AI created more structure than the assignment needed: both a `report/` and a `reports/` folder, an extra `data/interim/` stage, `.gitkeep` files in every empty folder, and a `tests/` folder with a test suite.
- **How we noticed it was wrong:** Reviewing the structure, we asked what each part was for. Two folders with almost the same name were confusing, the assignment does not ask for tests, the folders are created automatically by the code (so `.gitkeep` is unnecessary), and an intermediate data stage added nothing for a dataset this size.
- **What we did instead:** We asked the AI to simplify: one `report/` folder (LaTeX source + generated figures and tables), only `data/raw/` and `data/processed/`, and no tests or `.gitkeep` files. Lesson: AI tools tend to produce "complete-looking" boilerplate; every piece must be justified by the project's actual needs.
