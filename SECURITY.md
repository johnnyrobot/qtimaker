# Security Policy

## Security model and intended use

QTI Maker is designed to run **locally on a single user's machine**. The web
interface ships with **no authentication, no rate limiting, and no upload
quotas**, and by default it binds to `localhost`.

**Do not expose the web interface to the public internet as-is.** If you choose
to host it for multiple users, securing the deployment is your responsibility —
add authentication, rate limiting, HTTPS/TLS, upload restrictions, and set the
`ALLOWED_ORIGINS` environment variable. See the "Hosting online" section of the
[README](README.md#hosting-online).

Reports about the lack of built-in authentication or rate limiting in the
local/default configuration are considered **out of scope**, as this is a
documented design decision for a local tool.

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.7.x   | ✅        |
| < 0.7   | ❌        |

Security fixes are applied to the latest release.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report privately using GitHub's
[private vulnerability reporting](https://github.com/johnnyrobot/qtimaker/security/advisories/new)
(the **Security → Report a vulnerability** tab on the repository). This keeps
the details confidential until a fix is available.

When reporting, please include:

- A description of the vulnerability and its impact.
- Steps to reproduce, or a proof of concept.
- Affected version(s) and environment.

We will acknowledge your report as soon as possible and keep you informed of the
progress toward a fix. Thank you for helping keep QTI Maker and its users safe.
