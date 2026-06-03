# Policy rule migration

When renaming or replacing rules, use stable **`id`** fields and deprecation metadata so CI and SARIF consumers can migrate.

## Deprecating a rule

```yaml
rules:
  old_login_check:
    id: NCC-OLD-LOGIN
    deprecated: true
    replaced_by: NCC-REQUIRE_CONSOLE_LOGIN
    description: (deprecated) Use console login rule instead
    severity: high
    scope: global
    required_conditions:
      - "login"
```

Effects:

- `validate-policies` marks the rule `[DEPRECATED]` in output
- Scan **warnings** list deprecated rule IDs and `replaced_by` targets
- JSON/HTML reports include `deprecated` and `replaced_by` on each rule result

## Renaming rule IDs

1. Add the new rule with the new `id`.
2. Set `deprecated: true` and `replaced_by: <new-id>` on the old rule for one release cycle.
3. Update CI dashboards / SARIF suppressions to the new `id`.
4. Remove the deprecated rule in the next **policy_pack_version** bump.

## Policy pack versioning

Bump `policy_pack_version` in YAML when:

- Adding or removing rules
- Changing severity or scope
- Breaking `id` values

Record changes in [CHANGELOG.md](../CHANGELOG.md). Baseline JSON (`write-baseline`) keys on `config_path` and violation counts—not rule IDs—so re-baseline after major pack upgrades.

Contact: Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
