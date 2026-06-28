# AGENTS.md

## Project Summary

adabraka-ui is a Rust GPUI component library with reusable UI primitives, demos, and docs.

## Local Commands

- `just build`
- `just test`
- `just clippy`
- `just fmt`
- `just run-example demo`
- `just run-example slider_styled_demo`
- `just list-examples`

## GitHub Actions Commands

- `just build-ci`
- `just test-ci`
- `just clippy-ci`
- `just fmt-check`
- `just clippy-strict` (future hard gate, not currently wired into CI)

GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners because the default GPUI Metal shader compilation path can fail when the Metal Toolchain is unavailable.

The `Justfile` is the canonical command source for local development and CI targets.

## Working Rules

- Keep changes small and scoped to the requested task.
- Do not delete, overwrite, or clean untracked files unless explicitly asked.
- Follow existing patterns in `src/` and `examples/`.
- Run `just fmt`, `just clippy`, and `just test` before finishing code changes.
- If you change build, test, lint, or format commands, update `Justfile`, `AGENTS.md`, `CLAUDE.md`, and `.github/workflows/ci.yml` together.
- The `agents-md` CI job validates that command docs, the Justfile, and workflow commands stay aligned.

## Repository Notes

- Some components require initialization in `src/lib.rs`.
- Examples follow the `<component>_styled_demo.rs` naming pattern.
