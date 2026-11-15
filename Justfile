set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

test:
    uv run pytest -v

lint:
    uv run ruff check .
    uv run ruff format --check .

# Cut a release: just release 1.3.2
# Bumps pyproject.toml + uv.lock, rolls the changelog, commits, tags and pushes.
# Pushing the v* tag triggers .github/workflows/release.yml (PyPI + attestations).
release version:
    #!/usr/bin/env bash
    set -euo pipefail
    version="{{ version }}"

    [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "version must look like 1.2.3"; exit 1; }
    [[ "$(git branch --show-current)" == "main" ]] || { echo "must be on main"; exit 1; }
    [[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean"; exit 1; }
    git fetch origin main --tags --quiet
    [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || { echo "main is not in sync with origin/main"; exit 1; }
    ! git rev-parse -q --verify "refs/tags/v$version" >/dev/null || { echo "tag v$version already exists"; exit 1; }
    grep -q '^Unreleased$' CHANGELOG.md || { echo "CHANGELOG.md has no 'Unreleased' section"; exit 1; }

    # Bump pyproject.toml and refresh uv.lock (CI runs `uv sync --locked`)
    uv version "$version"
    uv lock --check

    # Roll the changelog: Unreleased -> version, with a fresh Unreleased on top
    perl -0pi -e "s/^Unreleased\n/Unreleased\n\n$version\n/m" CHANGELOG.md

    just lint
    just test
    rm -rf dist
    uv build

    git add pyproject.toml uv.lock CHANGELOG.md
    git commit -m "Release $version"
    git tag -a "v$version" -m "v$version"

    git push origin main
    git push origin "v$version"
    echo "Released v$version - watch the workflow: gh run watch"
