# Releasing & maintaining `shiftaiagenticinfra-sdk-python`

This document is for **maintainers** taking over this repo. It explains how the SDK is structured, how we add API methods, how we bump versions, and how we **build and publish** to PyPI (the process we use today).

User-facing API usage stays in **README.md**.

---

> ### **Mandatory before any new release (PyPI or GitHub)**  
> **You must bump the version number** in every place listed under [Versioning](#versioning-files-that-must-stay-aligned) **before** you:
>
> - upload to **PyPI**, and  
> - **commit / tag / push** to **GitHub** for that release.
>
> If you skip this: PyPI rejects the upload (**“File already exists”** for the same version), or your **git tag / README** no longer match what users `pip install`. **Never push a release to PyPI or tag GitHub without a version bump first.**

---

## What this project is

| Item | Detail |
|------|--------|
| **PyPI name** | `shiftaiagenticinfra-sdk-python` (what users `pip install`) |
| **Import package** | `shiftai` (e.g. `from shiftai import ShiftaiagenticinfraClient`) |
| **Runtime** | Async client on **httpx**; Python **≥ 3.8** |
| **Live package** | https://pypi.org/project/shiftaiagenticinfra-sdk-python/ |

We ship **wheels** (`.whl`) and **sdists** (`.tar.gz`) via `python -m build`. Legacy **egg** installs are not what we publish; `pip` prefers wheels.

---

## Repository layout (where to work)

All packaging and source live under **`shiftaiagenticinfra-sdk-python/`** (this folder).

```
shiftaiagenticinfra-sdk-python/
  pyproject.toml          # Primary metadata: version, deps, setuptools package list
  setup.py                # Legacy setuptools; keep version in sync with pyproject.toml
  README.md               # End-user docs
  RELEASING.md            # This file
  shiftai/
    __init__.py           # Exports ShiftaiagenticinfraClient; bump __version__ on release (see checklist)
    client.py             # ShiftaiagenticinfraClient wires HttpClient + *Api classes
    http/
      http_client.py      # POST/GET, Api-Key header, dataclass JSON, errors
      exceptions.py
    models/
      __init__.py         # All request/response dataclasses (DTOs); field names match JSON (camelCase)
    api/
      __init__.py         # Re-exports *Api classes
      messages_api.py
      analytics_api.py
      …                     # One module per API area
      internal/
  tests/
```

---

## How we build SDK methods (convention)

When the **Agent Infra backend** adds or changes an HTTP API:

1. **DTOs** — Add or update `@dataclass` types in `shiftai/models/__init__.py`. Use **field names that match the JSON** the server expects or returns (e.g. `messageId`, `userEmail`, `userpreferences` where the API uses that spelling).
2. **HTTP** — Use `HttpClient` in `shiftai/http/http_client.py`: `post`, `get`, `post_map`, etc. Authenticated calls send the **`Api-Key`** header from the client’s API key.
3. **API class** — Add methods on the right `*Api` class (e.g. analytics under `AnalyticsApi`, messages under `MessagesApi`). Constructor receives `HttpClient`; methods are `async def` and call `self._http_client.…`.
4. **Client** — If there is a new top-level API surface, wire it in `shiftai/client.py` on `ShiftaiagenticinfraClient`.
5. **Docs** — Update **README.md** for new public methods and important behavior.
6. **Nested / odd responses** — If the body is not a flat dataclass (e.g. list vs object, nested dicts), follow patterns in `analytics_api.py` (`get_latest_feedbacks`, `_parse_user_preference_item`, etc.): `post_map` + small parser helpers.

Validation that mirrors the backend (required email, etc.) lives next to the public method or builder pattern you use.

---

## Versioning: files that must stay aligned

**This step is mandatory before PyPI upload and before pushing the release to GitHub** (see warning at the top of this document).

We bump the **same semantic version** in every place that exposes it, then build once.

| File | What to change |
|------|----------------|
| **`pyproject.toml`** | `[project].version = "x.y.z"` — **source of truth** for builds |
| **`setup.py`** | `version="x.y.z"` — must match `pyproject.toml` (still used by some tooling / `setup.py` flows) |
| **`shiftai/__init__.py`** | `__version__ = "x.y.z"` — should match PyPI so `import shiftai; shiftai.__version__` is correct |

Today we ship frequent **patch** bumps (`0.0.10` → `0.0.11`, etc.) for API and doc updates. Use **minor** when you add larger features; **major** for breaking public API changes.

---

## Prerequisites (machine of the maintainer)

```bash
python -m pip install --upgrade pip build twine
```

- **Python 3.8+** (matches `requires-python` in `pyproject.toml`).
- **`build`** — produces `dist/*.whl` and `dist/*.tar.gz`.
- **`twine`** — uploads to PyPI.

---

## Credentials (what you need and why)

| Credential | Why you need it |
|------------|------------------|
| **PyPI account** (theshiftai / ShiftAI org) | Owns the project on PyPI; add new maintainers here; recover access. |
| **PyPI API token** (scoped to `shiftaiagenticinfra-sdk-python` if possible) | **Uploads:** PyPI does not accept your account password for `twine upload`. Create the token under **pypi.org → Account settings → API tokens**. For Twine, username is always **`__token__`**; at the password prompt you paste the **`pypi-…`** token. |

Do not commit tokens or `.pypirc` into this repository.

---

## Release procedure (what we do each time)

Work in a shell whose **current directory** is **`shiftaiagenticinfra-sdk-python`** (where `pyproject.toml` is).

### 1. Bump version (all three places above)

Example: `0.0.11` → `0.0.12`.

### 2. Commit & tag (recommended)

```bash
git add -A
git commit -m "Release 0.0.12"
git tag v0.0.12
```

### 3. Clean old artifacts (recommended)

Avoid uploading stale wheels from a previous version.

**Windows (PowerShell):**

```powershell
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

**macOS / Linux:**

```bash
rm -rf dist build *.egg-info
```

### 4. Build

```bash
python -m build
```

Check **`dist/`**: you should see one `.whl` and one `.tar.gz` for the **new** version only.

### 5. Check metadata

```bash
python -m twine check dist/*
```

Fix any reported issues in `pyproject.toml` / README, then rebuild.

### 6. Upload to PyPI

Upload uses **Twine**. PyPI expects username **`__token__`** and “password” = your **API token** (the `pypi-…` string from **Account settings → API tokens** on pypi.org).

**Step A — one-time (per machine)**  
Create a file named `.pypirc` in your **user home** (not inside this git repo):

| OS | Path |
|----|------|
| Windows | `%USERPROFILE%\.pypirc` |
| macOS / Linux | `~/.pypirc` |

File contents. Do **not** add a `password` line (the token is entered only when Twine prompts; it is not stored in this file):

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
```

**Step B — every release**  
From the `shiftaiagenticinfra-sdk-python` folder, after build and `twine check`:

```bash
python -m twine upload dist/*
```

When prompted for **Password**, paste the full **PyPI API token** and press Enter.  
If you are also prompted for **Username**, type exactly: `__token__`

### 7. Verify

- Open https://pypi.org/project/shiftaiagenticinfra-sdk-python/ and confirm the new version.
- In a **fresh venv**: `python -m pip install -U shiftaiagenticinfra-sdk-python` and smoke-test `from shiftai import ShiftaiagenticinfraClient`.
- `git push` and `git push origin v0.0.12` (or your remote/branch policy).

---

## Packaging notes specific to this repo

- **Build backend:** `setuptools.build_meta` (see `[build-system]` in `pyproject.toml`).
- **Packages included:** Listed under `[tool.setuptools] packages = […]` — if you add a new subpackage under `shiftai/`, add it there or installs will miss modules.
- **`[project.optional-dependencies] dev`** — pytest stack for local testing; not required for end users.
- **Egg-info / build folders** — Created locally after `build` or editable installs; safe to delete before release (see clean step).

---

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| **403 / invalid credentials** | Twine username must be `__token__`; password is the full API token, not the PyPI login password. |
| **400 File already exists** | That version string is already on PyPI — bump version again and rebuild. |
| **Import errors after install** | New package under `shiftai/` not listed in `[tool.setuptools] packages` — fix `pyproject.toml` and re-release. |
| **`__version__` wrong in Python** | Bump `shiftai/__init__.py` `__version__` to match `pyproject.toml`. |

---

## Maintainer checklist (copy for each release)

- [ ] **Version bumped (mandatory)** — `pyproject.toml`, `setup.py`, `shiftai/__init__.py` all same new version **before** PyPI/GitHub  
- [ ] README / code updated for any API changes  
- [ ] `rm -rf dist build *.egg-info` (or Windows equivalent)  
- [ ] `python -m build`  
- [ ] `python -m twine check dist/*`  
- [ ] `python -m twine upload dist/*` → at **Password**, paste **PyPI API token** (with `~/.pypirc` as above)  
- [ ] Verify on PyPI + `pip install -U` smoke test  
- [ ] Git commit + tag + push **after** version bump and successful release  

---

For **how to call each API** after install, see **README.md**. For **how the HTTP layer behaves**, read `shiftai/http/http_client.py`.
