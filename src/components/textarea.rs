//! Textarea component - Multi-line text input component with full editing capabilities.

use crate::components::input::InputVariant;
use crate::components::textarea_state::TextareaEvent;
use crate::components::textarea_state::TextareaState;
use crate::theme::use_theme;
use gpui::{prelude::FluentBuilder as _, *};
use std::rc::Rc;

/// Initialize textarea component with key bindings
pub fn init(cx: &mut App) {
    if !crate::initialization::begin(cx, "textarea") {
        return;
    }
    crate::components::textarea_state::init(cx);
}

#[derive(IntoElement)]
pub struct Textarea {
    state: Entity<TextareaState>,
    placeholder: SharedString,
    variant: InputVariant,
    disabled: bool,
    error: bool,
    rows: usize,
    min_rows: Option<usize>,
    max_rows: Option<usize>,
    auto_grow: bool,
    initial_value: Option<SharedString>,

    on_change: Option<Rc<dyn Fn(SharedString, &mut App)>>,
    on_enter: Option<Rc<dyn Fn(SharedString, &mut App)>>,
    on_shift_enter: Option<Rc<dyn Fn(SharedString, &mut App)>>,
    on_focus: Option<Rc<dyn Fn(SharedString, &mut App)>>,
    on_blur: Option<Rc<dyn Fn(SharedString, &mut App)>>,

    style: StyleRefinement,
}

impl Textarea {
    pub fn new(state: &Entity<TextareaState>) -> Self {
        Self {
            state: state.clone(),
            placeholder: "".into(),
            variant: InputVariant::Default,
            disabled: false,
            error: false,
            rows: 3,
            min_rows: None,
            max_rows: None,
            auto_grow: false,
            initial_value: None,
            on_change: None,
            on_enter: None,
            on_shift_enter: None,
            on_focus: None,
            on_blur: None,
            style: StyleRefinement::default(),
        }
    }

    pub fn value(mut self, value: impl Into<SharedString>) -> Self {
        self.initial_value = Some(value.into());
        self
    }

    pub fn placeholder(mut self, placeholder: impl Into<SharedString>) -> Self {
        self.placeholder = placeholder.into();
        self
    }

    pub fn variant(mut self, variant: InputVariant) -> Self {
        self.variant = variant;
        self
    }

    pub fn disabled(mut self, disabled: bool) -> Self {
        self.disabled = disabled;
        self
    }

    pub fn error(mut self, error: bool) -> Self {
        self.error = error;
        self
    }

    pub fn rows(mut self, rows: usize) -> Self {
        self.rows = rows.max(1);
        self
    }

    pub fn min_rows(mut self, min_rows: usize) -> Self {
        self.min_rows = Some(min_rows.max(1));
        self
    }

    pub fn max_rows(mut self, max_rows: usize) -> Self {
        self.max_rows = Some(max_rows.max(1));
        self
    }

    pub fn auto_grow(mut self, auto_grow: bool) -> Self {
        self.auto_grow = auto_grow;
        self
    }

    pub fn on_change<F>(mut self, callback: F) -> Self
    where
        F: Fn(SharedString, &mut App) + 'static,
    {
        self.on_change = Some(Rc::new(callback));
        self
    }

    pub fn on_enter<F>(mut self, callback: F) -> Self
    where
        F: Fn(SharedString, &mut App) + 'static,
    {
        self.on_enter = Some(Rc::new(callback));
        self
    }

    pub fn on_shift_enter<F>(mut self, callback: F) -> Self
    where
        F: Fn(SharedString, &mut App) + 'static,
    {
        self.on_shift_enter = Some(Rc::new(callback));
        self
    }

    pub fn on_focus<F>(mut self, callback: F) -> Self
    where
        F: Fn(SharedString, &mut App) + 'static,
    {
        self.on_focus = Some(Rc::new(callback));
        self
    }

    pub fn on_blur<F>(mut self, callback: F) -> Self
    where
        F: Fn(SharedString, &mut App) + 'static,
    {
        self.on_blur = Some(Rc::new(callback));
        self
    }

    fn calculate_height(&self, window: &Window, cx: &App) -> Pixels {
        let line_height = window.line_height().to_f64() as f32;
        let padding_y = 8.0;
        let base_height = self.rows as f32 * line_height + padding_y * 2.0;

        if self.auto_grow {
            let visual_lines = self.state.read(cx).visual_line_count_for_layout().max(1);
            let content_height = visual_lines as f32 * line_height + padding_y * 2.0;

            let final_height = if let Some(min_rows) = self.min_rows {
                let min_height = min_rows as f32 * line_height + padding_y * 2.0;
                content_height.max(min_height)
            } else {
                content_height.max(base_height)
            };

            if let Some(max_rows) = self.max_rows {
                let max_height = max_rows as f32 * line_height + padding_y * 2.0;
                px(final_height.min(max_height))
            } else {
                px(final_height)
            }
        } else {
            px(base_height)
        }
    }
}

impl Styled for Textarea {
    fn style(&mut self) -> &mut StyleRefinement {
        &mut self.style
    }
}

impl RenderOnce for Textarea {
    fn render(self, window: &mut Window, cx: &mut App) -> impl IntoElement {
        let theme = use_theme(cx);
        let height = self.calculate_height(window, cx);

        // Update state with properties
        self.state.update(cx, |state, cx| {
            state.disabled = self.disabled;
            state.placeholder = self.placeholder.clone();

            if !state.initialized {
                state.initialized = true;
                if let Some(value) = self.initial_value.clone() {
                    state.set_value(value, window, cx);
                }
            }
        });

        // Event subscriptions (same pattern as Input component)
        let on_change_callback = self.on_change.clone();
        let on_enter_callback = self.on_enter.clone();
        let on_shift_enter_callback = self.on_shift_enter.clone();
        let on_focus_callback = self.on_focus.clone();
        let on_blur_callback = self.on_blur.clone();

        if on_change_callback.is_some()
            || on_enter_callback.is_some()
            || on_shift_enter_callback.is_some()
            || on_focus_callback.is_some()
            || on_blur_callback.is_some()
        {
            let state_entity = self.state.clone();
            let state_for_callback = state_entity.clone();
            cx.subscribe(
                &state_entity,
                move |_emitter: Entity<TextareaState>, event: &TextareaEvent, cx: &mut App| {
                    match event {
                        TextareaEvent::Change => {
                            if let Some(callback) = on_change_callback.as_ref() {
                                let value = state_for_callback.read(cx).content.clone();
                                callback(value, cx);
                            }
                        }
                        TextareaEvent::Enter => {
                            if let Some(callback) = on_enter_callback.as_ref() {
                                let value = state_for_callback.read(cx).content.clone();
                                callback(value, cx);
                            }
                        }
                        TextareaEvent::ShiftEnter => {
                            if let Some(callback) = on_shift_enter_callback.as_ref() {
                                let value = state_for_callback.read(cx).content.clone();
                                callback(value, cx);
                            }
                        }
                        TextareaEvent::Focus => {
                            if let Some(callback) = on_focus_callback.as_ref() {
                                let value = state_for_callback.read(cx).content.clone();
                                callback(value, cx);
                            }
                        }
                        TextareaEvent::Blur => {
                            if let Some(callback) = on_blur_callback.as_ref() {
                                let value = state_for_callback.read(cx).content.clone();
                                callback(value, cx);
                            }
                        }
                        _ => {}
                    }
                },
            )
            .detach();
        }

        let (bg_color, border_color, text_color) = if self.disabled {
            (
                theme.tokens.muted.opacity(0.5),
                theme.tokens.border,
                theme.tokens.muted_foreground,
            )
        } else if self.error {
            match self.variant {
                InputVariant::Default => (
                    theme.tokens.background,
                    theme.tokens.destructive,
                    theme.tokens.foreground,
                ),
                InputVariant::Outline => (
                    theme.tokens.background,
                    theme.tokens.destructive,
                    theme.tokens.foreground,
                ),
                InputVariant::Ghost => (
                    gpui::transparent_black(),
                    theme.tokens.destructive.opacity(0.3),
                    theme.tokens.foreground,
                ),
            }
        } else {
            match self.variant {
                InputVariant::Default => (
                    theme.tokens.background,
                    theme.tokens.input,
                    theme.tokens.foreground,
                ),
                InputVariant::Outline => (
                    theme.tokens.background,
                    theme.tokens.border,
                    theme.tokens.foreground,
                ),
                InputVariant::Ghost => (
                    gpui::transparent_black(),
                    theme.tokens.border.opacity(0.3),
                    theme.tokens.foreground,
                ),
            }
        };

        let is_focused = self.state.read(cx).focus_handle(cx).is_focused(window);
        let focus_handle = self
            .state
            .read(cx)
            .focus_handle(cx)
            .tab_index(0)
            .tab_stop(true);
        let focus_handle_for_mouse = focus_handle.clone();
        let scroll_handle = self.state.read(cx).scroll_handle.clone();
        let user_style = self.style;

        div()
            .id(("textarea", self.state.entity_id()))
            .key_context("Textarea")
            .track_focus(&focus_handle)
            .track_scroll(&scroll_handle)
            .overflow_y_scroll()
            .when(!self.disabled, |this| {
                this.on_mouse_down(MouseButton::Left, {
                    let focus_handle = focus_handle_for_mouse.clone();
                    move |_event, window, _cx| {
                        window.focus(&focus_handle);
                    }
                })
            })
            .w_full()
            .h(height)
            .flex_shrink_0()
            .when(self.auto_grow, |this| this.min_h(height))
            .px(px(12.0))
            .py(px(8.0))
            .bg(bg_color)
            .border_1()
            .border_color(border_color)
            .rounded(theme.tokens.radius_md)
            .text_size(px(14.0))
            .font_family(theme.tokens.font_mono.clone())
            .text_color(text_color)
            .when(!self.disabled, |this| {
                this.hover(|style| {
                    style.border_color(if self.error {
                        theme.tokens.destructive
                    } else {
                        theme.tokens.ring
                    })
                })
            })
            .when(is_focused && !self.disabled, |this| {
                this.border_color(if self.error {
                    theme.tokens.destructive
                } else {
                    theme.tokens.ring
                })
            })
            .when(!self.disabled, |this| {
                this.on_action(window.listener_for(&self.state, TextareaState::backspace))
                    .on_action(window.listener_for(&self.state, TextareaState::delete))
                    .on_action(window.listener_for(&self.state, TextareaState::left))
                    .on_action(window.listener_for(&self.state, TextareaState::right))
                    .on_action(window.listener_for(&self.state, TextareaState::up))
                    .on_action(window.listener_for(&self.state, TextareaState::down))
                    .on_action(window.listener_for(&self.state, TextareaState::select_left))
                    .on_action(window.listener_for(&self.state, TextareaState::select_right))
                    .on_action(window.listener_for(&self.state, TextareaState::select_up))
                    .on_action(window.listener_for(&self.state, TextareaState::select_down))
                    .on_action(window.listener_for(&self.state, TextareaState::select_all))
                    .on_action(window.listener_for(&self.state, TextareaState::home))
                    .on_action(window.listener_for(&self.state, TextareaState::end))
                    .on_action(window.listener_for(&self.state, TextareaState::copy))
                    .on_action(window.listener_for(&self.state, TextareaState::cut))
                    .on_action(window.listener_for(&self.state, TextareaState::paste))
                    .on_action(window.listener_for(&self.state, TextareaState::enter))
                    .on_action(window.listener_for(&self.state, TextareaState::shift_enter))
                    .on_action(window.listener_for(&self.state, TextareaState::tab))
                    .on_action(window.listener_for(&self.state, TextareaState::shift_tab))
                    .on_action(window.listener_for(&self.state, TextareaState::escape))
                    .on_action(window.listener_for(&self.state, TextareaState::word_left))
                    .on_action(window.listener_for(&self.state, TextareaState::word_right))
                    .on_action(window.listener_for(&self.state, TextareaState::select_word_left))
                    .on_action(window.listener_for(&self.state, TextareaState::select_word_right))
            })
            .when(!self.disabled, |this| this.cursor(gpui::CursorStyle::IBeam))
            .map(|this| {
                let mut div = this;
                div.style().refine(&user_style);
                div
            })
            .child(self.state.clone())
    }
}
