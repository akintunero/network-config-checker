# Product scope and matching model

**Maintainer:** Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

## Supported input (v2.1)

| Supported | Not supported |
|-----------|----------------|
| Cisco IOS / IOS-XE `show running-config` plain text | Juniper `set` configuration |
| Interface blocks (`interface GigabitEthernet…`) | Arista EOS JSON exports |
| Global lines (hostname, SSH, HTTP, VTY, …) | OpenConfig / YANG payloads |
| Offline files in Git (`.cfg`, `.conf`, `.txt`) | Real-time SMU/state database |

The parser detects unsupported formats and adds **warnings** to reports (scan still runs; results may be incomplete).

## Condition matching (not a full config engine)

Policies use **phrase-aware regex**, not a vendor configuration tree:

| Prefix | Behavior |
|--------|----------|
| _(default)_ | Multi-word phrases with flexible whitespace; single tokens use word boundaries |
| `regex:` | Full regular expression on normalized text |
| `not:` | Negated phrase or `not:regex:…` |
| `substring:` | Legacy loose substring (opt-in for edge cases) |

Normalization collapses whitespace to a single line before matching. This reduces false positives (e.g. `login` vs unrelated tokens) but cannot model hierarchy, policy maps, or route-policy logic like NSO/ANSIBLE+JSON Schema.

For SMU-level guarantees, integrate this tool as a **Git gate** alongside your source-of-truth automation platform.

## Configuration directories

| Path | Purpose |
|------|---------|
| [`configs/`](../configs/) | **Production path** — fleet backups scanned in CI (`config-compliance.yml`) |
| [`config_samples/`](../config_samples/) | Noncompliant fixture only (`noncompliant_config.txt`) for tests |

Scan with **all** builtin packs:

```bash
network-config-checker scan -c configs -p policies/builtin -o reports --fail-on high
```

## File size limit

Each configuration file is limited to **5 MiB** by default (`--max-config-mib` to adjust). Prevents accidental CI DoS from huge pasted configs.
