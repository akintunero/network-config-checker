# Policy authoring guide

**Maintainer:** Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

## Policy pack structure

```yaml
policy_pack_name: my_baseline
policy_pack_version: "1.0.0"
rules:
  rule_key:
    id: NCC-RULE_KEY
    description: Human-readable intent
    severity: critical | high | medium | low
    scope: global | interface | vlan
    conditions: []              # all must match
    required_conditions: []     # each must match
    forbidden_conditions: []     # none may match
    remediation: |
      configuration snippet to apply
    references:
      - "CIS or NIST citation"
    vendor: cisco_ios
```

At least one of `conditions`, `required_conditions`, or `forbidden_conditions` is required per rule.

## Scopes

| Scope | Evaluated against |
|-------|-------------------|
| `global` | Configuration text outside interface blocks (hostname, SSH, HTTP, VTY, …) |
| `interface` | Each `interface …` stanza |
| `vlan` | Each `vlan …` stanza |

## Condition prefixes

Validated at load time against [policy.schema.json](../policies/schema/policy.schema.json) (JSON Schema).

| Prefix | Example | Behavior |
|--------|---------|----------|
| _(default)_ | `ip ssh version 2` | Phrase match with flexible whitespace; single words use word boundaries |
| `regex:` | `regex:hostname\\s+\\S+` | Regular expression on normalized text |
| `not:` | `not:ip http server` | Must **not** appear (phrase or `not:regex:…`) |
| `substring:` | `substring:legacy` | Loose substring (explicit opt-in) |

Optional rule lifecycle fields: `deprecated: true`, `replaced_by: NCC-NEW-RULE-ID` — see [POLICY_MIGRATION.md](POLICY_MIGRATION.md).

## Validate and explain

```bash
network-config-checker validate-policies -p policies/builtin/cisco_ios_baseline.yaml
network-config-checker policy explain -p builtin/cisco_ios_baseline --rule-id NCC-REQUIRE_HOSTNAME
```

JSON Schema: [policies/schema/policy.schema.json](../policies/schema/policy.schema.json)
