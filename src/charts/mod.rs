//! Compatibility facade for legacy chart paths.

pub use crate::capabilities::data::{
    area_chart, bar_chart, chart, donut_chart, gauge, heatmap, line_chart, pie_chart, radar_chart,
    treemap,
};

pub use bar_chart::{BarChart, BarChartData, BarChartMode, BarChartOrientation, BarChartSeries};
pub use chart::{
    Axis, AxisPosition, Chart, ChartArea, ChartPadding, DataPoint, DataRange, Legend,
    LegendPosition, Series, SeriesType, TooltipConfig,
};
pub use line_chart::{LineChart, LineChartPoint, LineChartSeries};
pub use pie_chart::{
    PieChart, PieChartLabelPosition, PieChartSegment, PieChartSize, PieChartVariant,
};
