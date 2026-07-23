//! Compatibility facade for legacy overlay paths.

pub use crate::capabilities::navigation::command_palette;
pub use crate::capabilities::overlays::{
    alert_dialog, bottom_sheet, context_menu, dialog, hover_card, popover, popover_menu, sheet,
    toast,
};

pub use alert_dialog::{init_alert_dialog, AlertDialog};
pub use bottom_sheet::{BottomSheet, BottomSheetSize};
pub use command_palette::{
    CloseCommand, Command, CommandPalette, CommandPaletteState, NavigateDown, NavigateUp,
    SelectCommand,
};
pub use context_menu::{ContextMenu, ContextMenuItem};
pub use dialog::{init_dialog, Dialog, DialogSize};
pub use hover_card::{HoverCard, HoverCardAlignment, HoverCardPosition};
pub use popover_menu::{PopoverMenu, PopoverMenuItem};
pub use sheet::{init_sheet, Sheet, SheetSide, SheetSize};
