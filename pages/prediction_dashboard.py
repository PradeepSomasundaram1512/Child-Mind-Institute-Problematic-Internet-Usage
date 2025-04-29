from dash import dcc, html, register_page
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import dash_table

register_page(__name__, path="/predictions")

# Load data
test_df = pd.read_csv("child-mind-institute-problematic-internet-use/test.csv")
pred_df = pd.read_csv("child-mind-institute-problematic-internet-use/submission.csv")

# Round predictions and merge
pred_df["sii"] = pred_df["sii"].round().astype(int)
merged_df = pd.merge(test_df, pred_df, on="id")

# Add helper columns
merged_df["gender_label"] = merged_df["Basic_Demos-Sex"].map({0: "Female", 1: "Male"})
merged_df["age_group"] = pd.cut(merged_df["Basic_Demos-Age"], bins=[4, 12, 18, 22],
                                labels=["Child", "Teen", "Adult"])

# SII Prediction Distribution (Enhanced)
fig_sii = px.histogram(
    merged_df,
    x="sii",
    color="sii",
    title="Predicted SII Level Distribution",
    labels={"sii": "Predicted SII"},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_sii.update_traces(marker_line_color="black", marker_line_width=1.5)
fig_sii.update_layout(
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#ffffff",
    xaxis=dict(title="SII Level", tickmode="linear"),
    yaxis_title="Participant Count",
    bargap=0.25,
    title_font_size=18
)

# Gender Pie (Enhanced)
fig_gender = px.pie(
    merged_df,
    names="gender_label",
    title="Gender Composition",
    color_discrete_sequence=px.colors.qualitative.Set1,
    hole=0.3
)
fig_gender.update_traces(
    textposition='inside',
    textinfo='percent+label',
    marker=dict(line=dict(color='#000000', width=1))
)
fig_gender.update_layout(
    title_font_size=18,
    showlegend=False,
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff"
)

# Age Group Pie (Enhanced with Legend)
fig_age = px.pie(
    merged_df,
    names="age_group",
    title="Age Group Distribution",
    color_discrete_sequence=px.colors.qualitative.Set3,
    hole=0.3
)
fig_age.update_traces(
    textposition='inside',
    textinfo='percent+label',
    marker=dict(line=dict(color='#000000', width=1))
)
fig_age.update_layout(
    title_font_size=18,
    showlegend=False,
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff"
)

# Table
table = dash_table.DataTable(
    data=merged_df[["id", "Basic_Demos-Age", "gender_label", "sii"]].to_dict("records"),
    columns=[
        {"name": "ID", "id": "id"},
        {"name": "Age", "id": "Basic_Demos-Age"},
        {"name": "Gender", "id": "gender_label"},
        {"name": "Predicted SII", "id": "sii"},
    ],
    page_size=10,
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "center", "padding": "8px"},
    style_header={"backgroundColor": "#f0f0f0", "fontWeight": "bold"},
)

# Layout
layout = dmc.Container(fluid=True, children=[
    dmc.Title("Final Predictions Dashboard", order=2),
    dmc.Space(h=20),

    dmc.SimpleGrid(cols=2, spacing="lg", children=[
        dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
            dmc.Title("SII Prediction Distribution", order=4),
            dcc.Graph(figure=fig_sii, config={"displayModeBar": False})
        ]),
        dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
            dmc.Title("Gender Composition", order=4),
            dcc.Graph(figure=fig_gender, config={"displayModeBar": False})
        ])
    ]),

    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Age Group Distribution", order=4),
        dcc.Graph(figure=fig_age, config={"displayModeBar": False}),
        dmc.Group(justify="flex-start", mt=10, children=[
            dmc.Badge("Child", color=None, style={"backgroundColor": "#8dd3c7", "color": "#000"}, size="md"),
            dmc.Text("Ages 5–12", size="sm", style={"color": "#666", "marginLeft": "4px", "marginRight": "12px"}),

            dmc.Badge("Teen", color=None, style={"backgroundColor": "#ffffb3", "color": "#000"}, size="md"),
            dmc.Text("Ages 13–18", size="sm", style={"color": "#666", "marginLeft": "4px", "marginRight": "12px"}),

            dmc.Badge("Adult", color=None, style={"backgroundColor": "#bebada", "color": "#000"}, size="md"),
            dmc.Text("Ages 19–22", size="sm", style={"color": "#666", "marginLeft": "4px"})
        ])



    ]),

    dmc.Space(h=20),

    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Predicted SII Table", order=4),
        html.Div(table)
    ])
])
