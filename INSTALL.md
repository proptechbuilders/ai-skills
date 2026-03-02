# INSTALL.md

Use this guide to bootstrap the `skill-manager` skill into a fresh Codex environment, then use it to install other skills.

Repository source:
- `https://github.com/proptechbuilders/ai-skills`

## 1) Install `skill-manager` (single command)

Run this exactly:

```bash
git clone --depth 1 https://github.com/proptechbuilders/ai-skills.git /tmp/ai-skills && mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills" && cp -R /tmp/ai-skills/.codex/skills/skill-manager "${CODEX_HOME:-$HOME/.codex}/skills/skill-manager" && rm -rf /tmp/ai-skills
```

Then restart Codex so it can detect the new skill.

## 2) Use `skill-manager` to install other skills

Install a single skill:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --path skills/tests-proptech
```

Install a collection:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --collection collections/backend-testing.json
```

Update already installed skills:

```bash
${CODEX_HOME:-$HOME/.codex}/skills/skill-manager/scripts/skill-manager \
  --repo your-org/codex-skills \
  --collection collections/backend-testing.json \
  --update
```

## 3) Expected output

- Per-skill status (installed/updated/failed)
- Source repo and ref
- Final reminder: `Restart Codex to pick up new skills.`

## 4) Suggested prompt for another Codex-powered agent

> Read `INSTALL.md` in this repo and run the bootstrap command in section 1 to install `skill-manager`. Then use section 2 to install the required skills for this project.
