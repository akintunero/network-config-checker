# Security policy

**Maintainer:** Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

## Threat model

| Mode | Risk | Guidance |
|------|------|----------|
| Offline scan (default) | Low — reads local files only | Safe for CI and Git hooks |
| Live mode (`[live]`) | High — uses network credentials | Use vault-backed env vars; read-only operator account |
| Notifications (`[notify]`) | Medium — outbound webhooks/email | Store webhook URLs and SMTP secrets in CI secrets |

## Reporting vulnerabilities

Email **akintunero101@gmail.com** with:

- Affected version (`network-config-checker --version`)
- Reproduction steps
- Impact assessment

Do not open public issues for undisclosed security bugs.

## Secure usage

- Never commit device passwords or `enable` secrets.
- Use `NETCHECK_DEVICE_*` environment variables for live checks.
- Treat configuration backups as sensitive data in artifact storage.
- Review SARIF/HTML reports before publishing—they may quote live configuration lines.
