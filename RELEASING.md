# Releasing cannlytics

The runbook for every `1.0.x` release. Commands are for Windows
(`cmd.exe`); the steps are the same elsewhere. A release is the same
two files, built once from a clean clone, uploaded first to TestPyPI and
then to PyPI.

> **PyPI is permanent.** A version, once uploaded, can never be uploaded
> again, even after it is deleted. If anything is wrong at any step,
> do not try to replace the files: bump the version (`1.0.6`) and start
> over. That is what the third number is for.

## Before the first release (once)

1. **PyPI.** Sign in at <https://pypi.org> as an owner of the
   `cannlytics` project (check *Your projects*; it holds 0.0.17). Two-
   factor authentication must be on; uploads require it. Create an API
   token: *Account settings → API tokens → Add API token*, scope
   **Project: cannlytics**. Copy it (it starts `pypi-`); it is shown
   once.
2. **TestPyPI.** TestPyPI is a separate site with separate accounts.
   Register at <https://test.pypi.org/account/register/>, turn on two-
   factor authentication, and create a token with scope **Entire
   account** (the project does not exist there yet). After the first
   upload, replace it with a token scoped to the project.
3. Keep both tokens in a password manager, never in a file in a
   repository.

## 1. Prepare the release commit

1. Set the version in `cannlytics/__init__.py` (`__version__`): drop
   the `.dev0` that `main` carries between releases (`1.0.6.dev0`
   becomes `1.0.6`), and replace `Unreleased` in its `CHANGELOG.md`
   entry with the date. The test suite fails if the entry is missing.
2. Run the suite in your development environment and push:

   ```bat
   python -m pytest tests -q
   git add -A
   git commit -m "Release 1.0.5"
   git push origin main
   ```

## 2. Build from a clean clone

Build from a fresh clone of the pushed commit, never from the working
copy: then no untracked local file (a `.env`, the `cb/` and `ky/` COA
fixtures) can reach a distribution. `MANIFEST.in` excludes them too;
this is the second lock.

```bat
cd %TEMP%
rmdir /s /q cannlytics-release 2>nul
git clone https://github.com/cannlytics/cannlytics cannlytics-release
cd cannlytics-release
git log -1 --oneline
python -m venv .release
.release\Scripts\python -m pip install --upgrade pip build twine
.release\Scripts\python -m build
.release\Scripts\python -m twine check --strict dist\*
```

`git log` must show the commit you pushed. `twine check` must print
`PASSED` twice. Then look inside the source distribution; the only line
printed should be `.env.example`:

```bat
tar -tzf dist\cannlytics-1.0.5.tar.gz | findstr /i ".pdf .env /cb/ /ky/ .pem .key"
```

## 3. Smoke-test the built wheel

```bat
python -m venv %TEMP%\cv-local
%TEMP%\cv-local\Scripts\python -m pip install dist\cannlytics-1.0.5-py3-none-any.whl
%TEMP%\cv-local\Scripts\python tools\smoke_test.py --version 1.0.5
```

It must end with `PASSED`, and the path it prints must be inside
`cv-local`, not the clone (run it as a file, as here, not with
`python -c`).

## 4. Upload to TestPyPI

```bat
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-TestPyPI-token
.release\Scripts\python -m twine upload --repository testpypi dist\*
```

Open <https://test.pypi.org/project/cannlytics/> and check that the
README renders, its links work, and the sidebar shows the right
version, Python versions, and project links. Then install it. Install
the dependencies from PyPI first, and only `cannlytics` from TestPyPI
with `--no-deps`: anyone can publish anything to TestPyPI, so never let
pip resolve dependencies there.

```bat
python -m venv %TEMP%\cv-test
%TEMP%\cv-test\Scripts\python -m pip install "numpy>=1.26" "pandas>=2.2" python-dateutil python-dotenv requests tzdata
%TEMP%\cv-test\Scripts\python -m pip install --no-deps --index-url https://test.pypi.org/simple/ cannlytics==1.0.5
%TEMP%\cv-test\Scripts\python tools\smoke_test.py --version 1.0.5
```

If the upload is refused with `403`, the name `cannlytics` belongs to
another account on TestPyPI. Skip this step; steps 2 and 3 have already
checked the files.

## 5. Upload to PyPI

Upload the **same files**; do not rebuild.

```bat
set TWINE_PASSWORD=pypi-your-PyPI-token
.release\Scripts\python -m twine upload dist\*
set TWINE_PASSWORD=
```

## 6. Verify the release

```bat
python -m venv %TEMP%\cv-pypi
%TEMP%\cv-pypi\Scripts\python -m pip install cannlytics==1.0.5
%TEMP%\cv-pypi\Scripts\python tools\smoke_test.py --version 1.0.5
```

If pip cannot find the version yet, wait a minute: the index updates
shortly after an upload. Check <https://pypi.org/project/cannlytics/>
as in step 4. Optionally, check that every extra resolves on Windows:
`pip install "cannlytics[all]==1.0.5"` in another fresh environment.

## 7. Tag the release

Tag the commit that is now on PyPI and publish the notes:

```bat
git tag -a v1.0.5 -m "cannlytics 1.0.5"
git push origin v1.0.5
```

On GitHub, *Releases → Draft a new release*, choose the tag, and paste
the `CHANGELOG.md` entry.

## 8. After the release

- Set `__version__` to the next number as a development release,
  `1.0.6.dev0`, and add a `## [1.0.6] — Unreleased` entry. Anything
  installed from `main` (the website's `git+…@main` line, a colleague's
  checkout) then reports a version that sorts before 1.0.6 and after
  1.0.5, and can never be mistaken for the published release. Keep
  iterating under that number until the next release; a number is
  spent only by publishing it.
- Downstream, pin to the release: `cannlytics~=1.0.5` in the website's
  `requirements.txt` (replacing the `git+…@main` line) and
  `cannlytics>=1.0.5,<2` in each dataset repository.

## If something goes wrong

| Symptom | What to do |
|---|---|
| `File already exists` | That file name was uploaded before, even if since deleted. Bump the version and rebuild. |
| `403` on TestPyPI | The name belongs to another TestPyPI account. Skip TestPyPI (step 4). |
| `403` on PyPI | The token is not scoped to `cannlytics`, or the account is not an owner. |
| A defect found after upload | Do not delete the release. On PyPI, *Manage → Releases → Options → Yank*, give the reason, and publish the fix as the next version. A yanked version stays installable for anyone who pinned it exactly; pip no longer picks it otherwise. |

The old 0.0.17 can stay as it is, since pip now prefers 1.0.5. Yanking it
("superseded; does not run on Linux") is optional and harmless.

## Later: releases from a tag

`optional/.github/workflows/release.yml` in the 1.0.5 bundle automates
this runbook with PyPI's Trusted Publishing (no tokens on your machine).
When a `v*` tag is pushed, it runs the suite on Windows and Linux,
Python 3.11–3.14, builds once, checks that the tag matches
`__version__`, uploads to TestPyPI, then to PyPI. To enable it:

1. Copy the file to `.github/workflows/release.yml` in this repository.
2. In the repository's *Settings → Environments*, create `testpypi` and
   `pypi` (for `pypi`, add yourself as a required reviewer, so that
   every upload to PyPI waits for your approval).
3. On PyPI, *Your projects → cannlytics → Publishing → Add a trusted
   publisher*: owner `cannlytics`, repository `cannlytics`, workflow
   `release.yml`, environment `pypi`. Do the same on TestPyPI with
   environment `testpypi`.

A release is then: update the version and changelog, push, and push the
tag.
