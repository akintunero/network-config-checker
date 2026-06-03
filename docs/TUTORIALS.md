# Tutorials

**Author:** Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

## 1. Pull-request gate (Git)

Store router backups under `configs/` and fail the build on high-or-critical violations.
The repository workflow `.github/workflows/config-compliance.yml` runs on every PR that
touches `configs/**`:

```bash
network-config-checker validate-policies -p policies/builtin
network-config-checker scan \
  -c configs \
  -p policies/builtin \
  -o reports \
  --format sarif,junit \
  --fail-on high
```

Commit `reports/compliance_report.sarif` as a workflow artifact or upload via `github/codeql-action/upload-sarif`.

## 2. Quarterly audit (directory + inventory)

```bash
network-config-checker scan \
  --inventory configs/inventory.csv \
  -c . \
  -p policies/builtin \
  -o audit-2025-q2 \
  --format csv,html
```

## 3. Regression baseline in Git

Create a baseline after a known-good release:

```bash
network-config-checker write-baseline \
  -c configs/production/edge-sw-01.cfg \
  -p builtin/cisco_ios_baseline \
  -o baselines \
  --write-baseline-to baselines/summary.json
```

On later commits:

```bash
network-config-checker scan \
  -c configs \
  -p builtin/cisco_ios_baseline \
  --baseline baselines/summary.json \
  -o reports
```

Log output lists configs that gained violations since the baseline.

## 4. Pre-commit hook

```bash
pip install -e ".[dev]"
pre-commit install
```

The repository `.pre-commit-config.yaml` scans the [`configs/`](../configs/) tree with all packs in `policies/builtin/`.
