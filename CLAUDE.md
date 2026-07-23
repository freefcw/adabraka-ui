# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Local build (now supports stable Rust)
just build

# Local tests
just test

# Local lint
just clippy

# Format
just fmt

# GitHub Actions build/test/lint path
just build-ci
just test-ci
just clippy-ci
just fmt-check

# Future strict clippy gate
just clippy-strict

# Capability architecture contracts
just check-boundaries
just check-cargo-contract
just verify-capabilities-ci

# After an intentional Cargo feature or example-target change
just update-cargo-contract

# Run a specific example
just run-example <example_name>

# List available examples
just list-examples

# Common examples
just run-example demo          # Comprehensive demo
just run-example slider_styled_demo  # Slider component demo
```

GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners because the default GPUI Metal shader compilation path can fail when the Metal Toolchain is unavailable. `just clippy-strict` exists as the future hard gate, but CI currently uses `just clippy-ci` while the existing clippy debt is being paid down.

The `Justfile` is the canonical command source for local development and CI targets.

## Architecture

This is a GPUI component library (73+ components) inspired by shadcn/ui for building desktop applications in Rust.

### Module Structure

Canonical implementation ownership lives in the private `src/capabilities/` namespace:

- **`foundation/`** - Theme, fonts, extensions, HTTP, initialization guard, and utilities
- **`layout/`** - Generic stacks, grids, panels, containers, and masonry; not scrolling
- **`motion/`**, **`effects/`** - Animation mechanics and visual effects
- **`primitives/`**, **`scroll/`**, **`overlays/`**, **`controls/`** - The low-level UI stack
- **`navigation/`**, **`data/`**, **`content/`**, **`editor/`**, **`media/`** - Higher-level capabilities

The public `components`, `display`, `charts`, `navigation`, `overlays`, theme, motion, layout, and utility modules are compatibility facades. Keep those paths and `prelude.rs` stable for downstream users. Read `src/capabilities/mod.rs` before placing a new component, and run `just check-boundaries` after changing canonical imports.

When intentionally changing a Cargo feature or example target, run `just update-cargo-contract`, review `scripts/cargo_contract.json`, then run `just check-cargo-contract`.

### Key Patterns

**Builder Pattern**: All components use builder pattern for configuration:
```rust
Button::new("id", "Label")
    .variant(ButtonVariant::Primary)
    .size(ButtonSize::Lg)
    .on_click(|_, _, _| {})
```

**Entity-based State**: Complex components use `Entity<T>` for state management:
```rust
let slider_state = cx.new(|cx| SliderState::new(cx));
Slider::new(slider_state.clone()).show_value(true)
```

**Theme System**: Use `use_theme(cx)` for colors, never hardcode:
```rust
let theme = use_theme(cx);
div().bg(theme.tokens.background).text_color(theme.tokens.foreground)
```

**Styled Trait**: All components implement `Styled` for GPUI styling methods:
```rust
Slider::new(state).w(px(400.0)).p(px(16.0)).rounded(px(12.0))
```

### Component Initialization

Some components require initialization. `lib.rs:init()` owns the ordered, idempotent root sequence, while capability modules own individual initializers. Individual initializers remain available through their legacy public paths.

### Font Feature Flags

Bundled fonts are gated behind feature flags for binary size control:

- `bundled-fonts` (default) — all 6 font files (~2.1 MB)
- `bundled-fonts-inter` — Inter Regular + Medium + SemiBold + Bold
- `bundled-fonts-inter-minimal` — Inter Regular + SemiBold only
- `bundled-fonts-mono` — JetBrains Mono Regular only
- `bundled-fonts-mono-full` — JetBrains Mono Regular + Bold
- Individual: `font-inter-regular`, `font-inter-medium`, `font-inter-semibold`, `font-inter-bold`, `font-mono-regular`, `font-mono-bold`

Downstream crates can disable default fonts and register their own via `cx.text_system().add_fonts(...)`.

### Example Naming Convention

Examples follow `<component>_styled_demo.rs` pattern and demonstrate full Styled trait customization.
