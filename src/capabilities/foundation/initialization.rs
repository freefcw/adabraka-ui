use gpui::{App, Global};
use std::collections::HashSet;

#[derive(Default)]
struct InitializationState {
    installed: HashSet<&'static str>,
}

impl Global for InitializationState {}

pub(crate) fn begin(cx: &mut App, component: &'static str) -> bool {
    cx.default_global::<InitializationState>()
        .installed
        .insert(component)
}

#[cfg(test)]
mod tests {
    use super::begin;
    use gpui::TestApp;

    #[gpui::test]
    fn initialization_guard_is_idempotent_and_scoped_per_app() {
        let mut first = TestApp::new();
        let mut second = TestApp::new();

        assert!(first.update(|cx| begin(cx, "component")));
        assert!(!first.update(|cx| begin(cx, "component")));
        assert!(second.update(|cx| begin(cx, "component")));
    }
}
