#[cfg(feature = "editor")]
pub mod editor;

#[cfg(feature = "editor")]
pub(crate) fn init(cx: &mut gpui::App) {
    editor::init(cx);
}
