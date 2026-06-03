# Compatibility matrix

| Component | Supported versions |
|-----------|-------------------|
| Python | 3.11, 3.12, 3.13 |
| Config format | Cisco IOS / IOS-XE style plain text (`show running-config` exports) |
| Policy format | YAML 1.2 per `policies/schema/policy.schema.json` |
| Platforms | Linux, macOS, Windows (via Python) |
| Container | `python:3.12-slim` image (see `Dockerfile`) |

## Config sources

| Source | Support |
|--------|---------|
| Git-tracked `.cfg` / `.txt` files | Fully supported (primary workflow) |
| Directory glob | `*.cfg`, `*.conf`, `*.txt`, `*.config` |
| CSV inventory | Columns `hostname`, `path` (optional `vendor`) |
| Live device (`[live]` extra) | Netmiko `show running-config` via `NETCHECK_*` env vars |

## Not yet supported

- Juniper `set` syntax and Arista EOS native parsers (contributions welcome per vendor)
- Encrypted config blobs or binary archives

Contact: Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
