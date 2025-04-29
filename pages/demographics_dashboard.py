# demographics_dashboard.py (multi-page layout for DMC v1.1.0)

from dash import dcc, html, Input, Output, register_page, callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import load_train_data

register_page(__name__, path="/demographics")

pl_df = load_train_data("child-mind-institute-problematic-internet-use/train.csv")
df = pl_df.to_pandas()

def categorize_age(age):
    if age <= 12:
        return "Child (5-12)"
    elif age <= 18:
        return "Adolescent (13-18)"
    else:
        return "Adult (19-22)"

def create_figures(dataframe):
    gender_map = {0: "Female", 1: "Male"}
    dataframe['gender_label'] = dataframe['sex'].map(gender_map)
    dataframe['age_group'] = dataframe['age'].apply(categorize_age)

    age_mean_sii = dataframe.groupby('age')['sii'].mean()

    fig_age = make_subplots(specs=[[{"secondary_y": True}]])
    fig_age.add_trace(go.Histogram(x=dataframe['age'], nbinsx=20, marker_color='dodgerblue', opacity=0.6, name='Age Count'), secondary_y=False)
    fig_age.add_trace(go.Scatter(x=age_mean_sii.index, y=age_mean_sii.values, mode='lines+markers', name='Avg SII', marker_color='crimson'), secondary_y=True)
    fig_age.update_layout(bargap=0.2, legend=dict(y=1.1, x=0.5, xanchor='center', orientation='h'))
    fig_age.update_xaxes(title_text='Age')
    fig_age.update_yaxes(title_text='Participant Count', secondary_y=False)
    fig_age.update_yaxes(title_text='Avg SII', secondary_y=True)

    fig_gender = px.box(
        dataframe, x='gender_label', y='sii', color='gender_label',
        labels={'gender_label': 'Gender', 'sii': 'SII Score'},
        category_orders={'gender_label': ['Female', 'Male']}
    )
    fig_gender.update_layout(boxmode='group', legend_title_text='Gender')

    fig_agegroup = px.violin(
        dataframe, x='age_group', y='sii', color='age_group', box=True, points='suspectedoutliers',
        labels={'age_group': 'Age Group', 'sii': 'SII Score'}
    )
    fig_agegroup.update_layout(showlegend=False)

    return fig_age, fig_gender, fig_agegroup

initial_figs = create_figures(df)

layout = dmc.Container(fluid=True, children=[
    dmc.Title("Demographics & PIU Severity Dashboard", order=2),
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
                dmc.SegmentedControl(id="gender-filter", value="all",
                    data=[{"label": "All", "value": "all"},
                          {"label": "Male", "value": "M"},
                          {"label": "Female", "value": "F"}])
            ])
        ])
    ]),

    dmc.Space(h=20),
    html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "20px"}, children=[
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Age Distribution & SII Trend", order=4),
                dcc.Graph(id="age-dist-graph", figure=initial_figs[0], config={"displayModeBar": False})
            ])
        ]),
        html.Div(style={"flex": "1 1 500px", "minWidth": "300px"}, children=[
            dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
                dmc.Title("Gender-wise SII Comparison", order=4),
                dcc.Graph(id="gender-sii-graph", figure=initial_figs[1], config={"displayModeBar": False})
            ])
        ])
    ]),

    dmc.Space(h=20),
    dmc.Card(withBorder=True, shadow="sm", radius="md", p="md", children=[
        dmc.Title("Severity by Age Groups", order=4),
        dcc.Graph(id="agegroup-severity-graph", figure=initial_figs[2], config={"displayModeBar": False})
    ])
])

@callback(
    Output("age-dist-graph", "figure"),
    Output("gender-sii-graph", "figure"),
    Output("agegroup-severity-graph", "figure"),
    Input("age-range-slider", "value"),
    Input("gender-filter", "value")
)
def update_charts(age_range, gender):
    min_age, max_age = age_range
    filtered_df = df[(df['age'] >= min_age) & (df['age'] <= max_age)].copy()
    if gender == "M":
        filtered_df = filtered_df[filtered_df['sex'] == 1]
    elif gender == "F":
        filtered_df = filtered_df[filtered_df['sex'] == 0]
    return create_figures(filtered_df)
