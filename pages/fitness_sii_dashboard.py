# fitness_sii_dashboard.py (multi-page compatible & DMC v1.1.0 compliant)

from dash import dcc, html, Input, Output, register_page,callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from data_loader import load_train_data

register_page(__name__, path="/fitness")

pl_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv")
df = pl_df.to_pandas()

def categorize_age(age):
    if age <= 12:
        return "Child (5-12)"
    elif age <= 18:
        return "Adolescent (13-18)"
    else:
        return "Adult (19-22)"

def create_fitness_figures(dataframe):
    gender_map = {0: "Female", 1: "Male"}
    dataframe['gender_label'] = dataframe['sex'].map(gender_map)
    dataframe['age_group'] = dataframe['age'].apply(categorize_age)

    # Endurance vs SII (Scatter)
    fig_scatter = px.scatter(
        dataframe,
        x="Fitness_Endurance-Max_Stage", y="sii",
        color="gender_label",
        labels={"Fitness_Endurance-Max_Stage": "Max Endurance Stage", "sii": "SII"},
        title="Max Endurance Stage vs SII by Gender",
        opacity=0.7
    )

    # Avg Endurance by SII (Bar)
    fig_bar = px.bar(
        dataframe.groupby("sii")["Fitness_Endurance-Max_Stage"].mean().reset_index(),
        x="sii", y="Fitness_Endurance-Max_Stage",
        labels={"sii": "SII Level", "Fitness_Endurance-Max_Stage": "Avg Max Endurance Stage"},
        title="Average Max Endurance by SII Level"
    )

    # Violin plot of endurance time by SII
    dataframe["endurance_time"] = dataframe["Fitness_Endurance-Time_Mins"] + dataframe["Fitness_Endurance-Time_Sec"] / 60
    fig_violin = px.violin(
        dataframe, x="sii", y="endurance_time", color="gender_label",
        box=True, points="all",
        labels={"sii": "SII", "endurance_time": "Endurance Time (mins)"},
        title="Endurance Time Distribution by SII and Gender"
    )

    return fig_scatter, fig_bar, fig_violin

initial_figs = create_fitness_figures(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Physical Fitness & PIU Severity Dashboard", order=2),
    dmc.Space(h=20),
    html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "16px"}, children=[
        html.Div(style={"flex": "1 1 300px", "minWidth": "300px"}, children=[
            dmc.Stack(gap=5, children=[
                dmc.Text("Filter by Age Range:", style={"fontWeight": 500}),
                dmc.RangeSlider(
                    id="age-range-slider", min=int(df['age'].min()), max=int(df['age'].max()),
                    value=[int(df['age'].min()), int(df['age'].max())], step=1,
                    marks=[{"value": v, "label": str(v)} for v in range(int(df['age'].min()), int(df['age'].max())+1, 5)],
                    minRange=0
                )
            ])
        ]),
        html.Div(style={"flex": "1 1 300px", "minWidth": "300px"}, children=[
            dmc.Stack(gap=5, children=[
                dmc.Text("Gender:", style={"fontWeight": 500}),
                dmc.SegmentedControl(
                    id="gender-filter", value="all",
                    data=[{"label": "All", "value": "all"}, {"label": "Male", "value": "M"}, {"label": "Female", "value": "F"}]
                )
            ])
        ])
    ]),

    dmc.Space(h=20),
    html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "20px"}, children=[
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Max Stage vs SII", order=4),
                dcc.Graph(id="fitness-scatter", figure=initial_figs[0], config={"displayModeBar": False})
            ])
        ]),
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Avg Endurance by SII", order=4),
                dcc.Graph(id="fitness-bar", figure=initial_figs[1], config={"displayModeBar": False})
            ])
        ])
    ]),

    dmc.Space(h=20),
    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Endurance Time Distribution by SII", order=4),
        dcc.Graph(id="fitness-violin", figure=initial_figs[2], config={"displayModeBar": False})
    ])
])

@callback(
    Output("fitness-scatter", "figure"),
    Output("fitness-bar", "figure"),
    Output("fitness-violin", "figure"),
    Input("age-range-slider", "value"),
    Input("gender-filter", "value")
)
def update_fitness_charts(age_range, gender):
    min_age, max_age = age_range
    filtered_df = df[(df['age'] >= min_age) & (df['age'] <= max_age)].copy()
    if gender == "M":
        filtered_df = filtered_df[filtered_df['sex'] == 1]
    elif gender == "F":
        filtered_df = filtered_df[filtered_df['sex'] == 0]
    return create_fitness_figures(filtered_df)
