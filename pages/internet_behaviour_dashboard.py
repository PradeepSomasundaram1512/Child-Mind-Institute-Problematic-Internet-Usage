# pages/internet_behavior_dashboard.py

from dash import dcc, html, Input, Output, register_page, callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from data_loader import load_train_data

register_page(__name__, path="/internet")

# Load and preprocess data
pl_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv")
df = pl_df.to_pandas()

# Clean data
df = df[df["sii"].notna() & df["PreInt_EduHx-computerinternet_hoursday"].notna()]

def create_behavior_figures(dataframe):
    gender_map = {0: "Female", 1: "Male"}
    dataframe['gender_label'] = dataframe['sex'].map(gender_map)

    # Box plot of hours/day by SII
    fig_box = px.box(
        dataframe, x="sii", y="PreInt_EduHx-computerinternet_hoursday", color="gender_label",
        labels={"sii": "SII Level", "PreInt_EduHx-computerinternet_hoursday": "Internet Hours/Day"},
        title="Internet Use by SII Level and Gender"
    )

    # Bar chart of average hours/day by SII
    fig_bar = px.bar(
        dataframe.groupby("sii")["PreInt_EduHx-computerinternet_hoursday"].mean().reset_index(),
        x="sii", y="PreInt_EduHx-computerinternet_hoursday",
        labels={"sii": "SII Level", "PreInt_EduHx-computerinternet_hoursday": "Avg Internet Hours/Day"},
        title="Average Internet Use by SII Level"
    )

    # Line chart of avg usage by age
    fig_line = px.line(
        dataframe.groupby("age")["PreInt_EduHx-computerinternet_hoursday"].mean().reset_index(),
        x="age", y="PreInt_EduHx-computerinternet_hoursday",
        labels={"age": "Age", "PreInt_EduHx-computerinternet_hoursday": "Avg Hours/Day"},
        title="Average Internet Use by Age"
    )

    return fig_box, fig_bar, fig_line

initial_figs = create_behavior_figures(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Internet Usage Behavior & PIU Severity Dashboard", order=2),
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
                dmc.Title("Internet Use by SII", order=4),
                dcc.Graph(id="internet-box-graph", figure=initial_figs[0], config={"displayModeBar": False})
            ])
        ]),
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Avg Internet Hours by SII", order=4),
                dcc.Graph(id="internet-bar-graph", figure=initial_figs[1], config={"displayModeBar": False})
            ])
        ])
    ]),

    dmc.Space(h=20),
    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Avg Internet Use by Age", order=4),
        dcc.Graph(id="internet-line-graph", figure=initial_figs[2], config={"displayModeBar": False})
    ])
])

@callback(
    Output("internet-box-graph", "figure"),
    Output("internet-bar-graph", "figure"),
    Output("internet-line-graph", "figure"),
    Input("age-range-slider", "value"),
    Input("gender-filter", "value")
)
def update_behavior_figures(age_range, gender):
    min_age, max_age = age_range
    filtered_df = df[(df['age'] >= min_age) & (df['age'] <= max_age)].copy()
    if gender == "M":
        filtered_df = filtered_df[filtered_df['sex'] == 1]
    elif gender == "F":
        filtered_df = filtered_df[filtered_df['sex'] == 0]
    return create_behavior_figures(filtered_df)