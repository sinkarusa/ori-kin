from dash import dcc, html

from .config import COLOR_OPTIONS


def create_layout():
    return html.Div([
            html.H1("Pseudo-Dome Pattern Generator with Parameters"),
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Radius (r):"),
                        dcc.Input(id='radius-input', type='number', value=5, min=1, step=0.1)
                    ], style={'margin-bottom': '10px'}),
                    html.Div([
                        html.Label("Number of segments (n):"),
                        dcc.Input(id='segments-input', type='number', value=5, min=3, step=1)
                    ], style={'margin-bottom': '10px'}),
                    html.Label("Fold color 1:"),
                    dcc.Dropdown(id='fold-color-1-input', options=COLOR_OPTIONS, value='red', clearable=False),
                    html.Label("Fold color 2:"),
                    dcc.Dropdown(id='fold-color-2-input', options=COLOR_OPTIONS, value='blue', clearable=False),
                    html.Label("Radial line color:"),
                    dcc.Dropdown(id='radial-color-input', options=COLOR_OPTIONS, value='black', clearable=False),
                    html.Div([
                        html.Label("Fold line width:"),
                        dcc.Input(id='fold-width-input', type='number', value=2, min=1, step=1)
                    ], style={'margin-bottom': '10px'}),
                    html.Div([
                        html.Label("Radial line width:"),
                        dcc.Input(id='radial-width-input', type='number', value=1, min=1, step=1)
                    ], style={'margin-bottom': '10px'}),
                    html.Div([
            html.Button("Export SVG", id="export-button", n_clicks=0, style={'margin-right': '10px'}),
            html.Button("Export DXF", id="export-dxf-button", n_clicks=0),
            dcc.Download(id="download-svg"),
            dcc.Download(id="download-dxf")
        ], style={'margin-bottom': '10px'})
                ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    dcc.Graph(id='pattern-plot')
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    html.H3("Calculated Parameters:"),
                    html.Pre(id='parameter-display')
                ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '10px'})
            ], style={'display': 'flex', 'justify-content': 'space-between'})
        ])