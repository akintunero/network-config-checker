FROM python:3.12-slim

LABEL org.opencontainers.image.title="network-config-checker"
LABEL org.opencontainers.image.description="Offline compliance scanner for network configs in Git"
LABEL org.opencontainers.image.authors="Olúmáyòwá Akinkuehinmi <akintunero101@gmail.com>"

RUN useradd --create-home --uid 10001 scanner
WORKDIR /workspace

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY policies /app/policies
COPY configs /app/configs
COPY config_samples/noncompliant_config.txt /app/config_samples/noncompliant_config.txt

WORKDIR /app
RUN pip install --no-cache-dir .

USER scanner
WORKDIR /workspace
ENTRYPOINT ["network-config-checker"]
CMD ["scan", "-c", "configs", "-p", "policies/builtin", "-o", "reports", "--fail-on", "high"]
