# pages/body_composition_dashboard.py (multi-page compatible)

from dash import dcc, html, Input, Output, register_page, callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from data_loader import load_train_data

register_page(__name__, path="/bodycomp")

# Load and preprocess data
pl_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv")
df = pl_df.to_pandas()

def categorize_age(age):
    if age <= 12:
        return "Child (5-12)"
    elif age <= 18:
        return "Adolescent (13-18)"
    else:
        return "Adult (19-22)"

def create_body_figures(dataframe):
    gender_map = {0: "Female", 1: "Male"}
    dataframe['gender_label'] = dataframe['sex'].map(gender_map)
    dataframe['age_group'] = dataframe['age'].apply(categorize_age)

    # BMI vs SII (scatter)
    fig_bmi = px.scatter(
        dataframe, x="BIA-BIA_BMI", y="sii", color="gender_label",
        labels={"BIA-BIA_BMI": "BMI", "sii": "SII Score"},
        title="BMI vs SII by Gender"
    )

    # Average Body Fat % by SII
    fig_fat = px.bar(
        dataframe.groupby("sii")["BIA-BIA_Fat"].mean().reset_index(),
        x="sii", y="BIA-BIA_Fat",
        labels={"sii": "SII", "BIA-BIA_Fat": "Avg Body Fat %"},
        title="Average Body Fat Percentage by SII Level"
    )
    # Hydration Violin Plot
    # Remove extreme TBW values
    filtered_df = dataframe[dataframe["BIA-BIA_TBW"] < 130]

    fig_tbw = px.violin(
        filtered_df,
        x="sii", y="BIA-BIA_TBW", color="gender_label",
        box=True, points="all",
        labels={"sii": "SII Level", "BIA-BIA_TBW": "Total Body Water (kg)"},
        title="Total Body Water by SII Level and Gender"
    )



    return fig_bmi, fig_fat, fig_tbw

initial_figs = create_body_figures(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Body Composition & PIU Severity Dashboard", order=2),
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
                dmc.Title("BMI vs SII", order=4),
                dcc.Graph(id="bmi-sii-graph", figure=initial_figs[0], config={"displayModeBar": False})
            ])
        ]),
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Avg Body Fat % by SII", order=4),
                dcc.Graph(id="fat-sii-graph", figure=initial_figs[1], config={"displayModeBar": False})
            ])
        ])
    ]),

    dmc.Space(h=20),
    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
    dmc.Title("Total Body Water Distribution by SII", order=4),
    dcc.Graph(id="tbw-sii-graph", figure=initial_figs[2], config={"displayModeBar": False})

    ])
])

@callback(
    Output("bmi-sii-graph", "figure"),
    Output("fat-sii-graph", "figure"),
    Output("tbw-sii-graph", "figure"),
    Input("age-range-slider", "value"),
    Input("gender-filter", "value")
)
def update_body_figs(age_range, gender):
    min_age, max_age = age_range
    filtered_df = df[(df['age'] >= min_age) & (df['age'] <= max_age)].copy()
    if gender == "M":
        filtered_df = filtered_df[filtered_df['sex'] == 1]
    elif gender == "F":
        filtered_df = filtered_df[filtered_df['sex'] == 0]
    return create_body_figures(filtered_df)
