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

- **`components/`** - Core interactive elements (Button, Input, Slider, Select, Editor, etc.)
- **`display/`** - Presentation components (Table, DataTable, Card, Badge, Accordion)
- **`navigation/`** - Navigation components (Sidebar, Tabs, Menu, Toolbar, StatusBar, Tree)
- **`overlays/`** - Modal dialogs, popovers, tooltips, command palettes, toasts
- **`theme/`** - Design tokens and theming (light/dark variants)
- **`animations.rs`** - Animation presets and easing functions
- **`layout.rs`** - Layout utilities (VStack, HStack, Grid)
- **`prelude.rs`** - Common re-exports for end users

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

Some components require initialization in `lib.rs:init()`:
- `components::input::init(cx)`
- `components::select::init_select(cx)`
- `components::combobox::init_combobox(cx)`
- `components::editor::init(cx)`
- `navigation::sidebar::init_sidebar(cx)`
- `overlays::popover::init(cx)`

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
