# Collection Manifest Schema

Use collection files to install groups of skills in one command.

## File shape

```json
{
  "repo": "your-org/codex-skills",
  "ref": "main",
  "skills": [
    { "path": "skills/tests-proptech" },
    { "path": "skills/review-proptech" }
  ]
}
```

## Fields

- `repo` (optional): overrides CLI `--repo` when set.
- `ref` (optional): overrides CLI `--ref` when set.
- `skills` (required): array of objects.
- `skills[].path` (required): folder path in repository that must contain `SKILL.md`.

## Validation rules

- The manifest file must exist in the target repository.
- `skills` entries must be objects with `path`.
- Every resolved `path` must contain `SKILL.md`.
- Duplicate resulting skill names are de-duplicated by local directory name.

## Notes

- Place manifests under `collections/*.json` in the central skills repository.
- Use stable refs (tags/SHAs) for reproducible installs when needed.
