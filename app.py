# app.py

from dash import Dash, html, dcc
import dash_mantine_components as dmc
import dash
import os

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=dmc.Container(fluid=True, children=[
        dmc.Paper(
            shadow="sm", bg="gray.1", radius=0, p="md", withBorder=True,
            children=[
                dmc.Group(align="center", justify="space-between", children=[
                    dmc.Group(align="center", children=[
                        dmc.Image(src=app.get_asset_url("thumbnail.jpg"), style={"width": "40px"}),
                        dmc.Title("Child Mind Institute — Problematic Internet Use", order=2)
                    ]),
                    dmc.Group(children=[
                        dcc.Link(dmc.Button("Predictions", variant="light"), href="/predictions"),
                        dcc.Link(dmc.Button("Demographics", variant="light"), href="/demographics"),
                        dcc.Link(dmc.Button("Fitness & SII", variant="light"), href="/fitness"),
                        dcc.Link(dmc.Button("Body Comp", variant="light"), href="/bodycomp"),
                        dcc.Link(dmc.Button("Psych Wellbeing", variant="light"), href="/psych"),
                        dcc.Link(dmc.Button("Internet Use", variant="light"), href="/internet"),
                        dcc.Link(dmc.Button("Actigraphy", variant="light"), href="/actigraphy")
                        

                    ])
                ])
            ]
        ),
        dmc.Space(h=20),
        dash.page_container
    ])
)

if __name__ == "__main__":
    app.run(debug=True)
