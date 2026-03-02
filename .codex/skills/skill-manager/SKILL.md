---
name: skill-manager
description: Install or update one or many Codex skills from a GitHub repository, including collection manifests for team bootstrap. Use when users ask to install skills by repo/path, refresh existing skills, or set up skill bundles on new machines.
---

# Skill Manager

Use this skill to install or update local Codex skills from a central GitHub repo into `${CODEX_HOME:-$HOME/.codex}/skills`.

## When to use

- Install one skill from GitHub path.
- Install multiple skills in one run.
- Install a named collection of skills from a manifest.
- Refresh already installed skills with `--update`.
- Bootstrap a brand-new repo/machine with a one-liner.

## Inputs

- `--repo <owner/repo>` (required)
- `--ref <branch|tag|sha>` (optional, default `main`)
- Either:
  - `--path <skills/...>` (repeatable), or
  - `--collection <collections/...json>`
- `--dest <dir>` (optional, default `${CODEX_HOME:-$HOME/.codex}/skills`)
- `--update` (optional; required to overwrite existing skill dirs)

## Workflow

1. Validate arguments (`--repo`, path/collection selection).
2. Fetch repo at ref into a temp directory.
3. If `--collection` is provided, load manifest and resolve skill paths.
4. For each target skill path, require `SKILL.md` at source.
5. Copy skill folder into destination; refuse overwrite unless `--update`.
6. Print per-skill status, source repo/ref, and restart reminder.
7. Exit non-zero if any skill failed.

## Command

```bash
.codex/skills/skill-manager/scripts/skill-manager --repo your-org/codex-skills --path skills/tests-proptech
```

## Bootstrap this skill into a brand-new repo

```bash
git clone --depth 1 https://github.com/your-org/ai-skills.git /tmp/ai-skills && mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills" && cp -R /tmp/ai-skills/.codex/skills/skill-manager "${CODEX_HOME:-$HOME/.codex}/skills/skill-manager" && rm -rf /tmp/ai-skills
```

Then restart Codex.

## Examples

Install one skill:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --path skills/tests-proptech
```

Install multiple skills:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --path skills/tests-proptech \
  --path skills/review-proptech
```

Install a collection:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --collection collections/backend-testing.json
```

Update existing installs:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --collection collections/backend-testing.json \
  --update
```

## Collection schema

For manifest format and constraints, see `references/collection-schema.md`.
