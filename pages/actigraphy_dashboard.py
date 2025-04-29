# pages/actigraphy_dashboard.py

from dash import dcc, html, register_page
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from data_loader import batch_process_actigraphy_features, load_train_data

register_page(__name__, path="/actigraphy")

# Load data efficiently using batch processing
daily_df = batch_process_actigraphy_features("child-mind-institute-problematic-internet-use/series_train.parquet").to_pandas()
train_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv").to_pandas()

if "id" not in daily_df.columns:
    raise ValueError("No actigraphy features could be extracted. Check preprocessing or data paths.")

# Merge actigraphy features with train labels (SII etc.)
df = pd.merge(daily_df, train_df, on="id")

# KDE Plot: Mean Light
# Clip outliers and improve readability with log scale
df["mean_light_clipped"] = df["mean_light"].clip(upper=df["mean_light"].quantile(0.95))
def kde_plot(dataframe, column, label):
    groups = [dataframe[dataframe["sii"] == lvl][column] for lvl in sorted(dataframe["sii"].unique())]
    labels = [f"SII {lvl}" for lvl in sorted(dataframe["sii"].unique())]
    fig = ff.create_distplot(groups, labels, show_hist=False, show_rug=False)
    fig.update_layout(
        title=f"Distribution of {label} (Log Scale) across SII Levels",
        xaxis_type='log'
    )
    return fig

# Line Plot: Hourly ENMO pattern
def time_trend_plot(dataframe, metric):
    df_hour = dataframe.copy()
    print("df_hour columns:", df_hour.columns)

    if "hour" not in df_hour.columns:
        df_hour["hour"] = ((df_hour["day"] / 1e9) // 3600).astype(int) % 24

    avg_hourly = df_hour.groupby(["hour", "sii"])[metric].mean().reset_index()

    fig = px.line(
        avg_hourly, x="hour", y=metric, color="sii",
        title=f"{metric.title()} Pattern by Hour and SII",
        labels={"hour": "Hour of Day", metric: metric.title()}
    )
    return fig


# Violin plot: Nighttime Activity %
def night_activity_violin(dataframe):
    fig = px.violin(
        dataframe, x="sii", y="percent_night_activity", box=True, points="all",
        title="Night Activity % across SII Levels",
        labels={"sii": "SII Level", "percent_night_activity": "Nighttime Activity (%)"}
    )
    return fig

# ENMO and Night Activity box plots
def create_main_charts(dataframe):
    fig_enmo = px.box(
        dataframe, x="sii", y="mean_enmo", color="sii",
        title="Daily Movement vs PIU Severity",
        labels={"sii": "SII Level", "mean_enmo": "Avg ENMO (Movement)"}
    )
    fig_night = px.box(
        dataframe, x="sii", y="percent_night_activity", color="sii",
        title="Nighttime Activity % vs PIU Severity",
        labels={"sii": "SII Level", "percent_night_activity": "% Night Activity"}
    )
    return fig_enmo, fig_night

fig_enmo, fig_night = create_main_charts(df)
fig_kde = kde_plot(df, "mean_light_clipped", "Mean Light")
fig_line = time_trend_plot(df, "mean_enmo")
fig_violin = night_activity_violin(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Actigraphy Patterns & PIU Severity Dashboard", order=2),
    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Daily Movement vs SII", order=4),
        dcc.Graph(figure=fig_enmo, config={"displayModeBar": False})
    ]),
    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Light Distribution by SII (KDE)", order=4),
        dcc.Graph(figure=fig_kde, config={"displayModeBar": False})
    ]),
    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("ENMO Hourly Pattern by SII", order=4),
        dcc.Graph(figure=fig_line, config={"displayModeBar": False})
    ]),
    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Night Activity % across SII Levels", order=4),
        dcc.Graph(figure=fig_violin, config={"displayModeBar": False})
    ])
])
