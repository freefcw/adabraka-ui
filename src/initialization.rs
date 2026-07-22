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
    use crate::{
        components::{
            date_picker::ClosePicker, image_viewer::ImageViewerClose, inline_edit::Save,
            mention_input::MentionConfirm, video_player::VideoPlayerTogglePlay,
        },
        navigation::tabs::TabNext,
        overlays::dialog::DialogCancel,
    };
    use gpui::{Action, App, TestApp};

    #[gpui::test]
    fn initialization_is_idempotent_and_scoped_per_app() {
        let mut first = TestApp::new();
        let mut second = TestApp::new();

        assert!(first.update(|cx| begin(cx, "component")));
        assert!(!first.update(|cx| begin(cx, "component")));
        assert!(second.update(|cx| begin(cx, "component")));
    }

    fn binding_count(cx: &App, action: &dyn Action) -> usize {
        cx.key_bindings()
            .borrow()
            .bindings_for_action(action)
            .count()
    }

    #[gpui::test]
    fn root_init_installs_component_bindings_once() {
        let mut app = TestApp::new();

        app.update(crate::init);
        app.read(|cx| {
            assert_eq!(binding_count(cx, &ClosePicker), 1);
            assert_eq!(binding_count(cx, &ImageViewerClose), 1);
            assert_eq!(binding_count(cx, &Save), 1);
            assert_eq!(binding_count(cx, &MentionConfirm), 1);
            assert_eq!(binding_count(cx, &VideoPlayerTogglePlay), 1);
            assert_eq!(binding_count(cx, &TabNext), 1);
            assert_eq!(binding_count(cx, &DialogCancel), 1);
        });

        app.update(crate::init);
        app.read(|cx| {
            assert_eq!(binding_count(cx, &ClosePicker), 1);
            assert_eq!(binding_count(cx, &ImageViewerClose), 1);
            assert_eq!(binding_count(cx, &Save), 1);
            assert_eq!(binding_count(cx, &MentionConfirm), 1);
            assert_eq!(binding_count(cx, &VideoPlayerTogglePlay), 1);
            assert_eq!(binding_count(cx, &TabNext), 1);
            assert_eq!(binding_count(cx, &DialogCancel), 1);
        });
    }
}
