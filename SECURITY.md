# Security

This repository is an evaluation pack. It must not contain credentials.

- Live runs take API keys from the process environment (`AZURE_OPENAI_*` or
  `OPENAI_API_KEY`). There is no repo-local `.env` loader.
- Do not commit `.env`, key files, Azure CLI caches, or `netrc`.
- `.env.example` lists variable names only.

Report issues privately to the ClaySeal maintainers rather than opening a
public issue that includes keys or customer data.
