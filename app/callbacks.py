import numpy as np
import plotly.graph_objs as go
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .layout import format_parameters
from .utils.barrel_vault import generate_barrel_vault_pattern
from .utils.calculations import (
    calculate_folding_angle,
    calculate_height,
    calculate_parameters,
    calculate_segment_angle,
    calculate_segment_length,
)
from .utils.export import create_dxf, create_svg
from .utils.pattern_generator import generate_pattern


def register_pseudo_dome_callbacks(app):  
    @app.callback(
        [Output('pattern-plot', 'figure'),
        Output('parameter-display', 'children')],
        [Input('radius-input', 'value'),
        Input('segments-input', 'value'),
        Input('fold-color-1-input', 'value'),
        Input('fold-color-2-input', 'value'),
        Input('radial-color-input', 'value'),
        Input('fold-width-input', 'value'),
        Input('radial-width-input', 'value')]
    )
    def update_pattern(r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width):
        
        """
        Callback function to update the pattern plot and parameter display.
        
        Args:
        r (float): Radius of the dome
        n (int): Number of segments
        fold_color_1 (str): First color for folds
        fold_color_2 (str): Seconds color for folds
        radial_color (str): Color for radial lines
        mv_width (float): Line width for mountain and valley folds
        radial_width (float): Line width for radial lines
        
        Returns:
        tuple: (Plotly figure, Parameter display string)
        """
        if r is None or n is None:
            return go.Figure(), "Please enter valid values for r and n."

        thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, num_radial_segments = calculate_parameters(r, n)
        traces = generate_pattern(r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width)

        layout = go.Layout(
            showlegend=False,
            yaxis=dict(scaleanchor="x", scaleratio=1),
            width=800,
            height=800,
            margin=dict(l=50, r=50, b=50, t=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        figure = {'data': traces, 'layout': layout}
        # Format folding angles in two aligned columns
        folding_angles = "\n".join([f"α{i+1}1: {np.degrees(a1):6.2f}°    α{i+1}2: {np.degrees(a2):6.2f}°" 
                                    for i, (a1, a2) in enumerate(alpha)])
        param_display = \
f"""
r: {r}
n: {n}
θ1: {np.degrees(theta1):.2f}°
θl: {np.degrees(theta_l):.2f}°
CD: {np.degrees(CD):.2f}°
α11: {np.degrees(alpha11):.2f}°

Number of radial segments: {num_radial_segments}

Segment angles (θi):
{', '.join([f'{np.degrees(theta):.2f}°' for theta in thetas])}

Segment lengths (si):
{', '.join([f'{length:.2f}' for length in s])}

β angles:
{', '.join([f'{np.degrees(angle):.2f}°' for angle in beta])}

a lengths:
{', '.join([f'{length:.2f}' for length in a])}

Folding angles (αi1, αi2):
{folding_angles}

Heights (hi):
{', '.join([f'{height:.2f}' for height in h])}
"""

        return figure, param_display

    @app.callback(
        Output("download-dxf", "data"),
        Input("export-dxf-button", "n_clicks"),
        [State('radius-input', 'value'),
        State('segments-input', 'value'),
        State('fold-color-1-input', 'value'),
        State('fold-color-2-input', 'value'),
        State('radial-color-input', 'value'),
        State('fold-width-input', 'value'),
        State('radial-width-input', 'value')],
        prevent_initial_call=True
    )
    def export_dxf(n_clicks, r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width):
        if n_clicks == 0:
            raise PreventUpdate
        
        buffer = create_dxf(r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width)
        return dcc.send_bytes(buffer.getvalue(), "pseudo_dome_pattern.dxf")

    @app.callback(
        Output("download-svg", "data"),
        Input("export-button", "n_clicks"),
        [State('radius-input', 'value'),
        State('segments-input', 'value'),
        Input('fold-color-1-input', 'value'),
        Input('fold-color-2-input', 'value'),
        State('radial-color-input', 'value'),
        State('fold-width-input', 'value'),
        State('radial-width-input', 'value')],
        prevent_initial_call=True
    )
    def export_svg(n_clicks, r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width):
        if n_clicks == 0:
            raise PreventUpdate
        
        svg_string = create_svg(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width)
        return dict(content=svg_string, filename="pseudo_dome_pattern.svg")


def register_barrel_vault_callbacks(app):
    @app.callback(
        [Output('barrel-pattern-plot', 'figure'),
        Output('barrel-parameter-display', 'children')],  # Changed to match new ID
        [Input('barrel-radius-input', 'value'),
        Input('barrel-segments-input', 'value'),
        Input('barrel-omega-input', 'value'),
        Input('barrel-fold-color-1-input', 'value'),
        Input('barrel-fold-color-2-input', 'value'),
        Input('barrel-connection-color-input', 'value'),
        Input('barrel-fold-width-input', 'value'),
        Input('barrel-connection-width-input', 'value')]
    )
    def update_barrel_vault_pattern(r, n, omega, fold_color_1, fold_color_2, 
                              connection_color, fold_width, connection_width):
        # Calculate parameters
        theta = calculate_segment_angle(omega, n)
        s = calculate_segment_length(r, theta)
        alpha = calculate_folding_angle(theta)
        h = calculate_height(s, alpha)
        
        total_width = n * s
        total_height = 2 * h
        
        # Generate pattern
        traces = generate_barrel_vault_pattern(r, n, omega)
        
        # Format parameters display
        parameters_text = format_parameters(r, n, omega, theta, s, alpha, h, total_width, total_height)
        
        layout = go.Layout(
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                range=[-h, total_width + h]
            ),
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                range=[-total_height/2 - h/2, total_height/2 + h]
            ),
            showlegend=False
        )
        
        return {'data': traces, 'layout': layout}, parameters_text

def register_callbacks(app):
    register_pseudo_dome_callbacks(app)
    register_barrel_vault_callbacks(app)