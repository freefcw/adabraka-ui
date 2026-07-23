pub mod audio_player;
pub mod canvas_component;
pub mod crop_area;
pub mod file_upload;
pub mod image_viewer;
#[cfg(feature = "qrcode")]
pub mod qr_code;
pub mod svg_renderer;
pub mod video_player;
pub mod waveform;

pub(crate) fn init_image(cx: &mut gpui::App) {
    image_viewer::init_image_viewer(cx);
}

pub(crate) fn init_video(cx: &mut gpui::App) {
    video_player::init_video_player(cx);
}
