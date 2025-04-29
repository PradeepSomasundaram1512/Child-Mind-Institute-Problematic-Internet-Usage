# pages/psych_wellbeing_dashboard.py (using grouped bar chart)

from dash import dcc, html, Input, Output, register_page, callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from data_loader import load_train_data

register_page(__name__, path="/psych")

# Load and preprocess data
pl_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv")
df = pl_df.to_pandas()

# Normalize scores between 0-100 for bar chart comparison
def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

def create_grouped_bar(dataframe):
    dataframe = dataframe[dataframe["sii"].notna()]
    dataframe['SDS_T_norm'] = normalize(dataframe['SDS-SDS_Total_T'])
    dataframe['SDS_Raw_norm'] = normalize(dataframe['SDS-SDS_Total_Raw'])
    dataframe['CGAS_norm'] = normalize(dataframe['CGAS-CGAS_Score'])

    categories = ['SDS_T_norm', 'SDS_Raw_norm', 'CGAS_norm']
    labels = {
        'SDS_T_norm': 'Depression (T-score)',
        'SDS_Raw_norm': 'Depression (Raw)',
        'CGAS_norm': 'Global Functioning'
    }

    melted = dataframe.groupby("sii")[categories].mean().reset_index().melt(id_vars="sii", var_name="Metric", value_name="Score")
    melted["Metric"] = melted["Metric"].map(labels)

    fig = px.bar(
        melted, x="sii", y="Score", color="Metric", barmode="group",
        title="Average Psychological Scores by SII Level",
        labels={"sii": "SII Level", "Score": "Normalized Score"}
    )
    return fig

initial_fig = create_grouped_bar(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Psychological Wellbeing & PIU Severity Dashboard", order=2),
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
    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Grouped Psychological Profile Chart", order=4),
        dcc.Graph(id="psych-bar-graph", figure=initial_fig, config={"displayModeBar": False})
    ])
])

@callback(
    Output("psych-bar-graph", "figure"),
    Input("age-range-slider", "value"),
    Input("gender-filter", "value")
)
def update_psych_chart(age_range, gender):
    min_age, max_age = age_range
    filtered_df = df[(df['age'] >= min_age) & (df['age'] <= max_age)].copy()
    if gender == "M":
        filtered_df = filtered_df[filtered_df['sex'] == 1]
    elif gender == "F":
        filtered_df = filtered_df[filtered_df['sex'] == 0]
    return create_grouped_bar(filtered_df)
