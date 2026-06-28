# Canonical command entry points for local development and CI.
# GitHub Actions uses gpui/runtime_shaders on hosted macOS runners because the
# default GPUI Metal shader compilation path can fail when the Metal Toolchain
# is unavailable.

cargo := env_var_or_default('CARGO', 'cargo')
runtime_shaders_feature := env_var_or_default('RUNTIME_SHADERS_FEATURE', 'gpui/runtime_shaders')

default:
    @just --list

build:
    {{ cargo }} build

test:
    {{ cargo }} test

clippy:
    {{ cargo }} clippy --all-targets

fmt:
    {{ cargo }} fmt

run-example example='':
    #!/usr/bin/env bash
    set -euo pipefail

    example="{{ example }}"
    if [ -z "$example" ]; then
      example="${EXAMPLE:-}"
    fi

    if [ -z "$example" ]; then
      echo "example is required, e.g. just run-example demo" >&2
      exit 1
    fi

    {{ cargo }} run --example "$example"

list-examples:
    #!/usr/bin/env bash
    set -euo pipefail

    find examples -maxdepth 1 -name '*.rs' -print \
      | sed 's#^examples/##; s#\.rs$##' \
      | sort

build-ci:
    {{ cargo }} build --features {{ runtime_shaders_feature }}

test-ci:
    {{ cargo }} test --features {{ runtime_shaders_feature }}

clippy-ci:
    {{ cargo }} clippy --all-targets --features {{ runtime_shaders_feature }}

# Strict clippy exists as the future hard gate, but CI uses clippy-ci while
# historical warnings are being paid down.
clippy-strict:
    {{ cargo }} clippy --all-targets --features {{ runtime_shaders_feature }} -- -D warnings

fmt-check:
    {{ cargo }} fmt --all --check

validate-agent-docs:
    #!/usr/bin/env bash
    set -euo pipefail

    summary="$(just --summary | tr ' ' '\n')"

    recipe_exists() {
      grep -Fx "$1" <<<"$summary" >/dev/null
    }

    for target in build test clippy fmt; do
      grep -Fqx -- "- \`just $target\`" AGENTS.md
      recipe_exists "$target"
    done

    grep -Fq -- "just run-example demo" AGENTS.md
    grep -Fq -- "just run-example slider_styled_demo" AGENTS.md
    grep -Fq -- "just list-examples" AGENTS.md
    grep -Fq -- "just list-examples" README.md
    grep -Fq -- "just run-example demo" CLAUDE.md
    grep -Fq -- "just run-example slider_styled_demo" CLAUDE.md
    grep -Fq -- "just list-examples" CLAUDE.md
    recipe_exists run-example
    recipe_exists list-examples

    for target in build-ci test-ci clippy-ci fmt-check; do
      grep -Fq -- "just $target" AGENTS.md
      grep -Fq -- "just $target" CLAUDE.md
      grep -Fq -- "target: $target" .github/workflows/ci.yml
      recipe_exists "$target"
    done

    grep -Fq -- 'run: just $' .github/workflows/ci.yml
    grep -Fq -- 'run: just validate-agent-docs' .github/workflows/ci.yml
    grep -Fq -- 'run: just check-clippy-policy' .github/workflows/ci.yml

    grep -Fq -- 'GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners' AGENTS.md
    grep -Fq -- 'GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners' CLAUDE.md
    grep -Fq -- 'The `Justfile` is the canonical command source' AGENTS.md
    grep -Fq -- 'The `Justfile` is the canonical command source' CLAUDE.md

    recipe_exists clippy-strict
    grep -Fq -- 'clippy-strict' AGENTS.md
    grep -Fq -- 'clippy-strict' CLAUDE.md

check-clippy-policy:
    #!/usr/bin/env bash
    set -euo pipefail

    summary="$(just --summary | tr ' ' '\n')"

    grep -Fq -- "target: clippy-ci" .github/workflows/ci.yml
    grep -Fx 'clippy-ci' <<<"$summary" >/dev/null
    grep -Fx 'clippy-strict' <<<"$summary" >/dev/null

    if grep -Fq -- "target: clippy-strict" .github/workflows/ci.yml; then
      echo "CI should continue to use the staged clippy-ci target until the warning debt is cleaned up."
      exit 1
    fi
