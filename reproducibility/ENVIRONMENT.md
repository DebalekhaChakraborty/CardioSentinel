# Environment

| | |
|---|---|
| Python | 3.12.6 |
| Packages | **335**, frozen |
| Digest | `installed_packages_sha256 = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` |

## Verify it, do not assume it

```bash
python -c "from cardiosentinel.neural.provenance import dependency_environment as d; print(d())"
```

**Verify with `dependency_environment()`, not a pip-freeze hash.** The digest is
computed over a normalised package snapshot; a freeze hash will not match and
its mismatch means nothing.

## Install

```bash
python -m pip install -e ".[dev,signal,ml,neural]"
```

## Rules

- **Never install, upgrade or downgrade** anything in the scientific
  environment. Every experiment lock binds this digest; changing it detaches the
  artifacts from their provenance.
- **No generative-model SDK is a project dependency.** The agents' provider
  adapters import lazily and are skipped when absent, so the deterministic path
  is always available.
