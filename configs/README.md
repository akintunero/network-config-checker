# Git-tracked network configurations

Store Cisco IOS-style `show running-config` exports here for compliance scanning in CI.

## Layout

| Path | Purpose |
|------|---------|
| `production/` | Production device backups committed from change windows |
| `lab/` | Lab and pre-production devices |
| `inventory.csv` | Optional fleet manifest (`hostname`, `path`, `vendor`) |

## Scan locally

All builtin policy packs (baseline + management hardening):

```bash
network-config-checker scan \
  -c configs \
  -p policies/builtin \
  -o reports \
  --format sarif,json,html \
  --fail-on high
```

Scan via inventory:

```bash
network-config-checker scan \
  --inventory configs/inventory.csv \
  -c . \
  -p policies/builtin \
  -o reports \
  --fail-on high
```

Single pack only:

```bash
network-config-checker scan \
  -c configs/production/edge-sw-01.cfg \
  -p builtin/cisco_ios_management_hardening \
  -o reports
```

## CI

Pull requests that touch `configs/**` run `.github/workflows/config-compliance.yml`.

Maintainer: **Olúmáyòwá Akinkuehinmi** — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
