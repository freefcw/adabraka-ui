//! External-consumer compatibility contract for the legacy public API.

#[allow(unused_imports)]
use adabraka_ui::{
    animate, animated_state, animation_coordinator, animations, charts, components,
    content_transition, display, fonts, gestures, gpui_ext, http, icon_config, layout, navigation,
    overlays, prelude, responsive, scroll_physics, spring, styled_ext, theme, transitions, util,
    virtual_list,
};

#[test]
fn legacy_root_modules_and_functions_remain_public() {
    let _ = std::any::type_name_of_val(&adabraka_ui::init);
    let _ = std::any::type_name_of_val(&adabraka_ui::init_http);
    let _ = std::any::type_name_of_val(&adabraka_ui::init_http_with_user_agent);
    let set_icon_base_path: fn(String) = adabraka_ui::set_icon_base_path;
    let _ = set_icon_base_path;
    let _ = std::any::type_name::<prelude::Button>();
}

#[test]
fn every_legacy_component_module_remains_public() {
    #[allow(unused_imports)]
    use components::{
        alert, animated_collapsible, animated_counter, animated_list, animated_presence,
        animated_progress, animated_switch, animated_text, audio_player, aurora, avatar,
        avatar_group, badge, button, calendar, canvas_component, carousel, checkbox, code_block,
        collapsible, color_picker, combobox, confetti, confirm_dialog, copy_button, countdown,
        crop_area, date_picker, dock, dot_pattern, drag_drop, drawer_navigation, dropdown,
        empty_state, expandable_card, file_upload, floating_action_button, form, glass_morphism,
        gradient_border, gradient_text, hotkey_input, icon, icon_button, icon_source, image_viewer,
        infinite_scroll, inline_edit, input, input_state, kbd, keyboard_shortcuts, label,
        layout_transition, magnetic_button, marquee, mention_input, meteors, navigation_menu,
        noise, notification_center, number_input, number_ticker, otp_input, pagination,
        particle_emitter, progress, pulse_indicator, radio, range_slider, rating, resizable,
        ripple, scrollable, scrollbar, search_input, segmented_nav, select, separator,
        shared_element_transition, shimmer, skeleton, skeleton_loader, slider, sortable_list,
        sparkline, spinner, split_pane, spotlight, stepper, svg_renderer, tag_input, text,
        text_field, text_highlight, text_reveal, textarea, textarea_state, tilt_card, time_picker,
        timeline, toggle, toggle_group, tooltip, type_writer, video_player, view_router, waveform,
    };
}

#[cfg(feature = "qrcode")]
#[test]
fn qrcode_legacy_module_remains_public() {
    let _ = std::any::type_name::<components::qr_code::QRCodeComponent>();
}

#[cfg(feature = "editor")]
#[test]
fn editor_legacy_module_remains_public() {
    let _ = std::any::type_name::<components::editor::Editor>();
}

#[test]
fn category_facades_and_direct_aliases_remain_public() {
    let _ = std::any::type_name::<charts::BarChart>();
    let _ = std::any::type_name::<overlays::CommandPalette>();
    let _ = std::any::type_name::<components::IconSize>();
    let _ = std::any::type_name::<components::IconVariant>();
    let _ = std::any::type_name::<components::IconSource>();
    let _ = std::any::type_name::<components::SliderAxis>();
    let _ = std::any::type_name::<components::badge::Badge>();
}

#[allow(unused_imports)]
mod prelude_export_contract {
    use adabraka_ui::prelude::{
        alert, animate_bounce_in, animate_fade_in, animate_fade_out, animate_scale_in,
        animate_slide_down, animate_slide_in_left, animate_slide_in_right, animate_slide_up, body,
        body_large, body_small, bounce, caption, code, code_small, current_breakpoint, ease_in_out,
        ease_out_quint, edit_menu, file_menu, h1, h2, h3, h4, h5, h6, help_menu, icon, icon_button,
        init_http, init_http_with_user_agent, init_image_viewer, init_mention_input,
        init_video_player, install_theme, label, label_small, lerp_color, lerp_f32, lerp_pixels,
        lerp_shadow, lerp_shadows, linear, muted, muted_small, pulsating_between, quadratic,
        responsive_columns, responsive_value, scrollable_both, scrollable_horizontal,
        scrollable_vertical, timeline, tooltip, use_theme, view_menu, window_menu, Accordion,
        AccordionItem, Alert, AlertDialog, AlertVariant, Align, AnimatedCollapsible,
        AnimatedCounter, AnimatedCounterState, AnimatedInteraction, AnimatedList,
        AnimatedListState, AnimatedPresence, AnimatedPresenceState, AnimatedProgress,
        AnimatedSwitch, AnimatedSwitchTransition, AnimatedText, AnimationCoordinator,
        AnimationPreset, AnimationRepeat, AppMenu, AppMenuBar, AreaChart, AreaChartMode,
        AreaChartSeries, AreaChartSize, AudioPlayer, AudioPlayerSize, AudioPlayerState, Aurora,
        Avatar, AvatarGroup, AvatarItem, AvatarSize, Axis, AxisPosition, Badge, BadgeVariant,
        BarChart, BarChartData, BarChartMode, BarChartOrientation, BarChartSeries, BottomSheet,
        BottomSheetSize, BreadcrumbItem, Breadcrumbs, Breakpoint, Button, ButtonSize,
        ButtonVariant, Calendar, CalendarLocale, CanvasComponent, Card, Carousel, CarouselSize,
        CarouselSlide, CarouselState, CarouselTransition, CellEditor, CellPosition, Chart,
        ChartArea, ChartPadding, Checkbox, CheckboxSize, CircularProgress, Cluster, CodeBlock,
        Collapsible, CollapsiblePane, ColorMode, ColorPicker, ColorPickerState, ColumnDef,
        Combobox, ComboboxEvent, ComboboxState, Command, CommandPalette, CommandPaletteState,
        Confetti, ConfettiState, Container, ContentTransition, ContentTransitionState, ContextMenu,
        CopyButton, CopyButtonState, Countdown, CountdownFormat, CountdownSeparator, CountdownSize,
        CountdownState, CropArea, CropAreaState, DataGrid, DataGridState, DataPoint, DataRange,
        DataTable, DateFormat, DatePicker, DatePickerState, DateValue, Dialog, DialogSize, Dock,
        DockState, DonutChart, DonutChartSize, DotPattern, DragData, DragHandle, Draggable,
        DrawerNavigation, DrawerSide, DrawerState, DropZone, DropZoneStyle, Dropdown,
        DropdownAlign, DropdownItem, DropdownState, EmptyState, EmptyStateSize, ExpandableCard,
        ExpandableCardState, FABSize, FABState, FileNode, FileNodeKind, FileTree, FileTypeFilter,
        FileUpload, FileUploadError, FileUploadSize, FileUploadState, FloatingActionButton, Flow,
        FlowDirection, Form, FormState, Gauge, GaugeSize, GestureDetector, GestureEvent,
        GlassIntensity, GlassMorphism, GradientBorder, GradientText, Grid, GridColumnDef,
        GridSortDirection, HStack, Heatmap, HotkeyInput, HotkeyInputState, HotkeyValue, HoverCard,
        HoverCardAlignment, HoverCardPosition, Html, Icon, IconButton, IconPosition, IconSize,
        IconSource, IconVariant, ImageItem, ImageViewer, ImageViewerSize, ImageViewerState,
        InfiniteScroll, InfiniteScrollState, InlineEdit, InlineEditState, InlineEditTrigger,
        Justify, KBDSize, KeyboardShortcuts, KeyframeAnimation, Label, LabelSide, LayoutAnimation,
        LayoutTransition, Legend, LegendPosition, LineChart, LineChartPoint, LineChartSeries,
        LoadingState, LongPressGesture, MagneticButton, MagneticButtonState, Markdown, Marquee,
        MarqueeDirection, MasonryGrid, MasonryItem, Mention, MentionInput, MentionInputEvent,
        MentionInputState, MentionItem, Menu, MenuBar, MenuBarItem, MenuItem, MenuItemKind,
        MeteorState, Meteors, NavigationMenu, NavigationMenuItem, Noise, NotificationBell,
        NotificationCenter, NotificationCenterState, NotificationItem, NotificationVariant,
        NumberInput, NumberInputSize, NumberInputState, NumberTicker, OTPInput, OTPInputEvent,
        OTPInputSize, OTPInputState, OTPState, PageTransition, Pagination, PanGesture, Panel,
        ParticleEmitter, ParticleEmitterConfig, ParticleEmitterState, PhysicsScrollState, PieChart,
        PieChartLabelPosition, PieChartSegment, PieChartSize, PieChartVariant, PlaybackSpeed,
        Popover, PopoverMenu, PopoverMenuItem, ProgressBar, ProgressSize, ProgressVariant,
        PulseIndicator, RadarChart, RadarChartSize, RadarDataset, Radio, RadioGroup, RadioLayout,
        RangeSlider, RangeSliderState, Rating, RatingSize, RatingState, ResizablePanel,
        ResizablePanelGroup, ResizableState, Responsive, RevealMode, RichBlock, RichInline,
        RichTableAlignment, Ripple, SVGRenderer, ScrollContainer, ScrollDirection, ScrollList,
        ScrollPhysics, SearchFilter, SearchInput, SearchInputState, SegmentedNav, SegmentedNavSize,
        SegmentedNavState, Select, SelectOption, SelectedFile, Separator, SeparatorOrientation,
        Series, SeriesType, SharedElementState, SharedElementTransition, Sheet, SheetSide,
        SheetSize, Shimmer, ShortcutCategory, ShortcutItem, Skeleton, SkeletonLoader,
        SkeletonLoaderState, SkeletonVariant, Slider, SliderAxis, SliderSize, SliderState,
        SortDirection, SortableList, SortableListState, Spacer, Sparkline, SparklineSize,
        SparklineTrend, SparklineVariant, Spinner, SpinnerSize, SpinnerVariant, SplitDirection,
        SplitPane, SplitPaneEvent, SplitPaneState, Spotlight, SpotlightState, Spring,
        StaggerConfig, StandardMacMenuBar, StatusBar, StatusItem, StepItem, StepStatus, Stepper,
        StepperOrientation, StepperSize, StepperState, StyledExt, SwipeDirection, SwipeGesture,
        TabItem, Table, TableColumn, TableRow, Tabs, TagInput, TagInputState, TapGesture, Text,
        TextAnimation, TextField, TextFieldSize, TextHighlight, TextReveal, TextVariant, Textarea,
        TextareaEvent, TextareaState, Theme, ThemeTokens, ThemeVariant, TiltCard, TiltCardState,
        TimeFormat, TimePeriod, TimePicker, TimePickerState, TimeUnits, TimeValue, Timeline,
        TimelineConnectorStyle, TimelineIndicatorStyle, TimelineItem, TimelineItemPosition,
        TimelineItemVariant, TimelineLayout, TimelineOrientation, TimelineSize, ToastItem,
        ToastManager, ToastPosition, ToastVariant, Toggle, ToggleGroup, ToggleGroupItem,
        ToggleGroupSize, ToggleGroupVariant, ToggleSize, Toolbar, ToolbarButton,
        ToolbarButtonVariant, ToolbarGroup, ToolbarItem, ToolbarSize, TooltipConfig, Transition,
        TreeList, TreeMap, TreeMapNode, TreeNode, TypeWriter, TypeWriterState, VStack,
        VideoPlaybackSpeed, VideoPlaybackState, VideoPlayer, VideoPlayerSize, VideoPlayerState,
        ViewRouter, ViewRouterState, Waveform, KBD,
    };

    #[cfg(feature = "qrcode")]
    use adabraka_ui::prelude::QRCodeComponent;
    #[cfg(feature = "editor")]
    use adabraka_ui::prelude::{Editor, EditorLanguage, EditorState};
}
