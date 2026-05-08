# Security Policy

## Scope

`agent-scaffold` is a CLI that asks an LLM to emit code and writes that code to the user's filesystem. The security surface includes:

- **Path-handling logic** in `contract.py` and `writer.py` — these enforce that LLM-emitted file paths stay inside the destination directory and refuse absolute, parent-relative, or symlink-escaping paths.
- **Project metadata in generated output** — `pyproject.toml`, `package.json`, `Dockerfile`, etc. emitted by the LLM. The CLI validates structure but does not sandbox-execute the generated code.
- **Bundled `agent-deployments` docs** — shipped inside the wheel; treated as trusted input.
- **Smoke check execution** — the optional `agent-scaffold validate --tier smoke` step runs commands defined by language YAMLs (`uv run pytest`, `npm test`, etc.) inside the generated project.

## Reporting a Vulnerability

If you find a security issue (e.g. path traversal in the writer, a way to make the contract validator accept escaping paths, command injection in a language YAML, or unsafe defaults users might copy into production), please report it responsibly rather than opening a public issue.

**How to report:**
1. Open a [GitHub Security Advisory](https://github.com/jagguvarma15/agent-scaffold/security/advisories/new) (preferred — keeps details private until resolved)
2. Or email the maintainer directly via the contact on their GitHub profile

**Please include:**
- The affected file path and line number, or the failing CLI invocation
- A reproduction (command + minimal recipe / language YAML / mocked LLM response)
- A description of the impact (what an attacker could read, write, or execute)
- A suggested fix if you have one

## Response

We aim to acknowledge reports within 3 business days and publish a fix or advisory within 14 days of confirmation.

## Out of Scope

- Vulnerabilities in third-party dependencies (Anthropic SDK, Typer, Pydantic, etc.) — report these upstream. We track CVEs and bump pins when relevant.
- Issues that require the user to deliberately point `--deployments-path` at an attacker-controlled directory containing malicious recipes. The CLI treats `agent-deployments` content as trusted input by design.
- Issues that only apply if the user runs `agent-scaffold validate --tier smoke` against generated code without reviewing it first. We recommend reviewing generated output before executing it.
