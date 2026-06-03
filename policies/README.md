# Policy packs (canonical source)

Edit YAML files only under **`policies/builtin/`**. They are installed with the package via `pyproject.toml` data-files (no duplicate copy under `src/`).

| Path | Purpose |
|------|---------|
| `builtin/*.yaml` | Builtin policy packs |
| `schema/policy.schema.json` | JSON Schema validated at load time |

After changing policies, run:

```bash
network-config-checker validate-policies -p policies/builtin
```
