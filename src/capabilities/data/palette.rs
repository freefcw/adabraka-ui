//! Shared chart palette so every chart component resolves the same color for a
//! given series index. Keeping this in one place means a palette change (for
//! example a dark-mode variant) only touches a single definition instead of
//! eight copy-pasted arrays.

use gpui::Hsla;

/// Default 8-color palette used by all chart components.
const CHART_COLORS: [u32; 8] = [
    0x3b82f6, 0x22c55e, 0xf59e0b, 0xef4444, 0x8b5cf6, 0x06b6d4, 0xf97316, 0xec4899,
];

/// Resolve the palette color for `index`, cycling through [`CHART_COLORS`].
pub(crate) fn default_color(index: usize) -> Hsla {
    gpui::rgb(CHART_COLORS[index % CHART_COLORS.len()]).into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cycles_through_palette_in_order() {
        let first = default_color(0);
        let second = default_color(1);
        let wrapped = default_color(CHART_COLORS.len());
        assert_eq!(first, default_color(0));
        assert_ne!(first, second);
        assert_eq!(wrapped, first);
    }

    #[test]
    fn handles_arbitrary_indices() {
        // should never panic on modulo
        let _ = default_color(usize::MAX);
        let _ = default_color(0);
    }
}
