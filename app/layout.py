from dash import dcc, html

from .config import COLOR_OPTIONS


def create_landing_layout():
    return html.Div([
        html.H1("ORI-KIN", style={'text-align': 'center', 'margin-bottom': '40px'}),
        html.Div([
            html.Div([
                html.H3("Pseudo-Dome Pattern Generator"),
                html.P("Generate patterns for creating pseudo-dome structures"),
                dcc.Link(
                    html.Button("Select", style={'width': '100%'}),
                    href='/pseudo-dome'
                )
            ], style={'width': '300px', 'padding': '20px', 'border': '1px solid #ddd', 'margin': '10px'}),
            
            html.Div([
                html.H3("Barrel Vault Pattern Generator"),
                html.P("Generate patterns for creating barrel vault structures"),
                dcc.Link(
                    html.Button("Select", style={'width': '100%'}),
                    href='/barrel-vault'
                )
            ], style={'width': '300px', 'padding': '20px', 'border': '1px solid #ddd', 'margin': '10px'})
        ], style={'display': 'flex', 'justify-content': 'center', 'gap': '20px'}),

        # Add your images below the buttons:
        html.Div(
            [
                html.Img(src='/assets/pseudo_dome.png', style={'width': '300px', 'margin': '20px'}),
                html.Img(src='/assets/barrel_vault.png', style={'width': '300px', 'margin': '20px'}),
            ],
            style={'display': 'flex', 'justify-content': 'center'}
        )
    ])

def create_pseudo_dome_layout():
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

def format_parameters(r, n, m, omega, theta, s, alpha,h_max, h, total_width, total_height):
    return f"""Input Parameters:
    Radius (r): {r:.2f}
    Number of segments (n): {n}
    Number of tiles (m): {m}
    Central angle (Ω): {omega:.2f}°

Calculated Parameters:
    Segment angle (θ): {theta:.2f}°
    Segment length (s): {s:.2f}
    Folding angle (α): {alpha:.2f}°
    Max Height (h_max): {h_max:.2f}
    Set Height (h): {h:.2f}

Pattern Properties:
    Total Width: {total_width:.2f}
    Total Height: {total_height:.2f}"""
    
def create_barrel_vault_layout():
    return html.Div([
        html.H1("Barrel Vault Pattern Generator"),
        html.Div([
            # Input controls column
            html.Div([
                html.Div([
                    html.Label("Radius (r):"),
                    dcc.Input(id='barrel-radius-input', type='number', value=2, min=1, step=0.1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Number of segments (n):"),
                    dcc.Input(id='barrel-segments-input', type='number', value=6, min=3, max=20,step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Number of tiles (m):"),
                    dcc.Input(id='barrel-tiles-input', type='number', value=1, min=1, max=20,step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Unit cell height (h) [clamped by hmax=tan(Ω/(2n))]:"),
                    dcc.Input(id='barrel-height-input', type='number', value=1, min=0, max=20,step=0.01)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Central angle (Ω):"),
                    dcc.Input(id='barrel-omega-input', type='number', value=180, min=1, max=360, step=1)
                ], style={'margin-bottom': '10px'}),
                html.Label("Fold color 1:"),
                dcc.Dropdown(id='barrel-fold-color-1-input', options=COLOR_OPTIONS, value='red', clearable=False),
                html.Label("Fold color 2:"),
                dcc.Dropdown(id='barrel-fold-color-2-input', options=COLOR_OPTIONS, value='blue', clearable=False),
                html.Label("Connection line color:"),
                dcc.Dropdown(id='barrel-connection-color-input', options=COLOR_OPTIONS, value='black', clearable=False),
                html.Div([
                    html.Label("Fold line width:"),
                    dcc.Input(id='barrel-fold-width-input', type='number', value=2, min=1, step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Connection line width:"),
                    dcc.Input(id='barrel-connection-width-input', type='number', value=1, min=1, step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Button("Export SVG", id="barrel-export-button", n_clicks=0, style={'margin-right': '10px'}),
                    html.Button("Export DXF", id="barrel-export-dxf-button", n_clicks=0),
                    dcc.Download(id="barrel-download-svg"),
                    dcc.Download(id="barrel-download-dxf")
                ], style={'margin-bottom': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

            # <---- Add your separator line here ---->
            html.Hr(),

            # <---- Instructions text block ---->
            html.Div([
                # You can either use a plain Div with line breaks:
                html.Div("Single-centered Barrel Vault Pattern Generator"),
                html.Div("Main Parameters"),
                html.Div("Radius"),
                html.Div("Number of segment"),
                html.Div("Central angle"),
                html.Div("Note: Omega=180 : Semicircle; Omega>180 : Horseshoe arch"),
                html.Br(),
                html.Div("Secondary parameters"),
                html.Div("Number of row"),
                html.Div("h value"),
                html.Div("Note:"),
                html.Div("h = max => triangular crease pattern"),
                html.Div("h < max => trapezoidal pattern"),
                html.Br(),
                html.Div("Drawing parameters"),
                html.Div("Fold color 1"),
                html.Div("Fold color 2"),
                html.Div("Connection line color"),
                html.Div("Fold line width"),
                html.Div("Connection line width"),
            ], style={'whiteSpace': 'pre-line', 'margin-top': '10px'}),
        
            # Plot column
            html.Div([
                dcc.Graph(id='barrel-pattern-plot')
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
            
            # Parameters display column
            html.Div([
                html.H3("Calculated Parameters:"),
                html.Pre(id='barrel-parameter-display')
            ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '10px'})
        ], style={'display': 'flex', 'justify-content': 'space-between'})
    ])
def create_parameters_display(r, n, m, omega, theta, s, alpha, h, total_width, total_height):
    return html.Div([
        html.H3("Pattern Parameters", style={'marginBottom': '20px'}),
        
        html.Div([
            html.H4("Input Parameters:", style={'color': '#666'}),
            html.Table([
                html.Tr([html.Td("Radius (r):"), html.Td(f"{r:.2f}")]),
                html.Tr([html.Td("Number of segments (n):"), html.Td(f"{n}")]),
                html.Tr([html.Td("Number of tiles (m):"), html.Td(f"{m}")]),
                html.Tr([html.Td("Central angle (Ω):"), html.Td(f"{omega:.2f}°")]),
            ], style={'width': '100%', 'marginBottom': '20px'}),
            
            html.H4("Calculated Parameters:", style={'color': '#666'}),
            html.Table([
                html.Tr([html.Td("Segment angle (θ):"), html.Td(f"{theta:.2f}°")]),
                html.Tr([html.Td("Segment length (s):"), html.Td(f"{s:.2f}")]),
                html.Tr([html.Td("Folding angle (α):"), html.Td(f"{alpha:.2f}°")]),
                html.Tr([html.Td("Height (h):"), html.Td(f"{h:.2f}")]),
            ], style={'width': '100%'}),
            
            html.H4("Pattern Properties:", style={'color': '#666', 'marginTop': '20px'}),
            html.Table([
                html.Tr([html.Td("Total Width:"), html.Td(f"{total_width:.2f}")]),
                html.Tr([html.Td("Total Height:"), html.Td(f"{total_height:.2f}")]),
            ], style={'width': '100%'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ])
# def create_barrel_vault_layout():
    return html.Div([
        html.H1("Barrel Vault Pattern Generator"),
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Radius (r):"),
                    dcc.Input(id='barrel-radius-input', type='number', value=5, min=1, step=0.1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Number of segments (n):"),
                    dcc.Input(id='barrel-segments-input', type='number', value=5, min=3, step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label("Central angle (Ω):"),
                    dcc.Input(id='barrel-omega-input', type='number', value=90, min=1, max=360, step=1)
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Button("Export SVG", id="barrel-export-button", n_clicks=0, style={'margin-right': '10px'}),
                    html.Button("Export DXF", id="barrel-export-dxf-button", n_clicks=0),
                    dcc.Download(id="barrel-download-svg"),
                    dcc.Download(id="barrel-download-dxf")
                ], style={'margin-bottom': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([
                dcc.Graph(id='barrel-pattern-plot')
            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        ])
    ])