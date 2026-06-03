# network-config-checker

**Offline compliance scanner for network configs in Git**

Scan Cisco IOS-style configuration backups against versioned YAML policy packs. Use it in pull requests, pre-commit hooks, and CI pipelines—no live device credentials required.

**Author:** [Olúmáyòwá Akinkuehinmi](mailto:akintunero101@gmail.com)  
**Repository:** [github.com/akintunero/network-config-checker](https://github.com/akintunero/network-config-checker)

---

## Features

- Offline analysis of `.cfg`, `.conf`, `.txt` configuration backups
- Built-in policy packs: `builtin/cisco_ios_baseline`, `builtin/cisco_ios_management_hardening`
- Git-tracked fleet directory: [`configs/`](configs/) (scanned automatically in CI)
- Policy scopes: `global`, `interface`, `vlan`
- Reports: TXT, JSON, HTML, CSV, **SARIF** (GitHub Code Scanning), **JUnit XML** (CI dashboards)
- Fleet scans via directory glob or CSV inventory
- Baseline/regression comparison for config drift in Git
- CI exit codes: `0` pass, `1` policy violations, `2` runtime error
- Optional extras: `[live]` Netmiko read-only checks, `[notify]` Slack/email alerts

---

## Quick start

```bash
git clone https://github.com/akintunero/network-config-checker.git
cd network-config-checker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Scan the Git-tracked fleet (recommended — both builtin packs):

```bash
network-config-checker scan \
  -c configs \
  -p policies/builtin \
  -o reports \
  --format txt,json,sarif \
  --fail-on high
```

Quick-start single file:

```bash
network-config-checker scan \
  -c configs/production/edge-sw-01.cfg \
  -p policies/builtin \
  -o reports
```

See [docs/SCOPE.md](docs/SCOPE.md) for supported vendors and matching behavior.

Scan every config in a directory:

Or use the fleet inventory:

```bash
network-config-checker scan \
  --inventory configs/inventory.csv \
  -c . \
  -p policies/builtin \
  -o reports \
  --fail-on high
```

---

## GitHub Actions

PRs that change `configs/**` run [`.github/workflows/config-compliance.yml`](.github/workflows/config-compliance.yml), which scans the full `configs/` tree against **all** packs in `policies/builtin/` and uploads SARIF.

Use the composite action from this repository:

```yaml
- uses: actions/checkout@v4
- uses: akintunero/network-config-checker@v2.1.0
  with:
    config-path: configs
    policy: policies/builtin
    fail-on: high
    formats: sarif,json,junit
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: reports/compliance_report.sarif
```

See [`.github/workflows/config-compliance.yml`](.github/workflows/config-compliance.yml) for a full workflow example.

---

## CLI reference

| Command | Purpose |
|---------|---------|
| `scan` | Scan file(s) against policies |
| `validate-policies` | Validate YAML policy syntax and schema |
| `policy explain --rule-id <ID>` | Print rule metadata and remediation |
| `write-baseline` | Emit JSON baseline for `--baseline` comparisons |

### `scan` options

| Flag | Description |
|------|-------------|
| `-c`, `--config` | File or directory of configs |
| `-p`, `--policy` | Policy file, directory, or `builtin/<pack>` |
| `-o`, `--output` | Report directory (default: `reports`) |
| `--format` | `txt,json,html,csv,sarif,junit` |
| `--fail-on` | `critical`, `high`, `medium`, `low` (default: `high`) |
| `--inventory` | CSV with `hostname,path` columns |
| `--baseline` | Compare against prior `write-baseline` JSON |
| `--write-baseline-to` | Save violation counts for drift detection |
| `--json-logs` | Structured JSON logging |
| `--max-config-mib` | Max size per config file (default: 5) |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success (no violations at/above `--fail-on`) |
| `1` | Policy violations detected |
| `2` | Misconfiguration or runtime error |

---

## Policy packs

| Pack | Focus |
|------|--------|
| `builtin/cisco_ios_baseline` | Hostname, HTTP/SSH, interfaces, telnet |
| `builtin/cisco_ios_management_hardening` | Enable secret, console login, logging, NTP, SNMP |

Use `policies/builtin` (directory) to merge every pack in CI. Example rule:

```yaml
policy_pack_name: cisco_ios_baseline
policy_pack_version: "1.0.0"
rules:
  require_hostname:
    id: NCC-REQUIRE_HOSTNAME
    description: Device must define a hostname
    severity: medium
    scope: global
    required_conditions:
      - "regex:hostname\\s+\\S+"
    remediation: |
      hostname edge-sw-01
    references:
      - "CIS Cisco IOS Benchmark — device identification"
```

See [docs/POLICY_AUTHORING.md](docs/POLICY_AUTHORING.md), [docs/POLICY_MIGRATION.md](docs/POLICY_MIGRATION.md), and [docs/RELEASE.md](docs/RELEASE.md).

---

## Project layout

```
network-config-checker/
├── src/network_config_checker/   # Application package
├── policies/builtin/             # Builtin policy packs
├── policies/schema/              # JSON Schema for policies
├── configs/                      # Git-tracked device configs (CI scanned)
├── config_samples/               # Noncompliant fixture for tests only
├── tests/                        # Pytest suite
├── docs/                         # Authoring and security guides
├── action.yml                    # GitHub composite action
└── Dockerfile                    # Container image
```

---

## Development

```bash
make install-dev
make check          # ruff + pytest
make scan           # sample compliant scan
```

Maintainer contact: **Olúmáyòwá Akinkuehinmi** — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

---

## Optional: live monitoring

Live mode requires the `[live]` extra and **environment variables** (never commit credentials):

```bash
export NETCHECK_DEVICE_HOST=203.0.113.10
export NETCHECK_DEVICE_USERNAME=netops
export NETCHECK_DEVICE_PASSWORD='use-a-vault-secret'
export NETCHECK_DEVICE_TYPE=cisco_ios
pip install -e ".[live]"
python -c "from network_config_checker.live import LiveMonitor, device_from_env; LiveMonitor(device_from_env(), 'builtin/cisco_ios_baseline').check_once()"
```

---

## License

MIT — see [LICENSE](LICENSE).
