# Releasing

Releases are built and published by `.github/workflows/publish.yml` when a
`vX.Y.Z` tag is pushed. Pull requests and manual runs build the same wheels and
sdist but never publish.

## One-time setup

- **Repository secret** `PYPI_API_TOKEN`: a PyPI API token. Scope it to the
  `puzzlekit` project (the project already exists on PyPI).
- **GitHub environment** `pypi` (Settings → Environments). The publish job
  runs in it, so you can require a manual approval before anything is uploaded.

## Before tagging

1. Set `version` in `pyproject.toml` to the release (for example `0.4.0`, not
   `0.4.0.dev0`). Keep `rust/Cargo.toml` in step.
2. Refresh the puzzle table if adapters or data changed:
   ```sh
   python scripts/puzzle_table.py collect          # needs sibling pzprjs and puzzlekit-dataset
   python scripts/puzzle_table.py render --write
   ```
3. Run `python -m pytest -q` with Node 24+ and a built custom pzprjs
   (`PUZZLEKIT_PZPRJS`), so the state checks are not skipped.
4. Open a pull request to `main`. Wait for **PR CI** and for the wheel matrix
   in **Build wheels and publish**. It builds one `abi3` wheel per platform
   (five in total) on Python 3.10, runs the tests in the build environment,
   then installs each wheel on Python 3.10, 3.12 and 3.14 and runs them again.

## Publish

```sh
git tag v0.4.0
git push origin v0.4.0
```

The workflow refuses to publish when the tag differs from the version in
`pyproject.toml`. After the wheels, sdist and tests pass, `twine check` runs
and the files are uploaded to PyPI.

PyPI never accepts the same version twice; a failed or wrong release needs a
new version number.

## After publishing

1. Check an install from PyPI in a clean environment:
   ```sh
   uv venv && uv pip install puzzlekit==0.4.0
   .venv/bin/python -c "import puzzlekit; print(puzzlekit.solve('https://puzz.link/p?nurikabe/2/2/1i').status)"
   ```
2. Create a GitHub release for the tag.
3. Run **Deploy Docs** to publish the documentation.
4. Bump `pyproject.toml` to the next `.dev0` version.

## Bumping pzprjs

The `pzpr-state` CI job builds a pinned revision of
[pzprjs-trace](https://github.com/SmilingWayne/pzprjs-trace)
(`PZPRJS_REF` in `ci_pr.yml`). Move the pin only after the state tests pass
against the new revision.
