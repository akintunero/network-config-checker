# Release and distribution

**Maintainer:** Olúmáyòwá Akinkuehinmi — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

## Versioning

This project follows [Semantic Versioning](https://semver.org/). Git tags use the `v` prefix (e.g. `v2.1.0`).

## Install from Git (recommended for CI)

```bash
pip install "network-config-checker @ git+https://github.com/akintunero/network-config-checker.git@v2.1.0"
```

Or check out the repository and run:

```bash
pip install -e .
```

## GitHub Action pinning

Pin the composite action to a release tag—not floating `@main` in production:

```yaml
- uses: akintunero/network-config-checker@v2.1.0
  with:
    config-path: configs
    policy: policies/builtin
```

The action installs the package from the checked-out tag at `${{ github.action_path }}`.

## PyPI (optional)

Maintainers can publish wheels with the **Release** workflow (`.github/workflows/release.yml`) after creating a signed tag:

```bash
git tag -s v2.1.0 -m "v2.1.0"
git push origin v2.1.0
```

Configure PyPI trusted publishing or `PYPI_API_TOKEN` in repository secrets for automated upload.

## Artifacts per release

- Python wheel + sdist (`dist/`)
- CycloneDX SBOM (`dist/sbom.cdx.json`)
- GitHub Release notes from tag message

## SARIF and GitHub Advanced Security

SARIF upload steps use `continue-on-error: true` so repositories without Code Scanning enabled still pass CI. Enable **Code scanning** under repository Security settings to surface findings in the GitHub UI.
