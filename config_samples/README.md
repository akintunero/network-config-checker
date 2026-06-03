# Configuration samples

| File | Purpose |
|------|---------|
| `noncompliant_config.txt` | Intentionally failing config for tests and `make scan-fail` |

**Compliant fleet configs** live in [`configs/`](../configs/) (production + lab). Do not duplicate them here.

Quick scan:

```bash
network-config-checker scan -c configs -p policies/builtin -o reports --fail-on high
```
