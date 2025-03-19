import numpy as np
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from .layout import format_parameters
from .utils.barrel_vault import generate_barrel_vault_pattern
from .utils.calculations import (
    calculate_folding_angle,
    calculate_height,
    calculate_parameters,
    calculate_segment_angle,
    calculate_segment_length,
)
from .utils.export import create_dxf, create_svg, create_barrel_vault_svg, create_barrel_vault_dxf
from .utils.pattern_generator import generate_pattern
from .utils.config_loader import get_pseudo_dome_config, get_barrel_vault_config


def register_pseudo_dome_callbacks(app):
    # Help modal callbacks
    @app.callback(
        Output("help-modal", "is_open"),
        [Input("radius-help-button", "n_clicks"), 
         Input("segments-help-button", "n_clicks"), 
         Input("close-help-modal", "n_clicks")],
        [State("help-modal", "is_open")],
    )
    def toggle_help_modal(radius_help_clicks, segments_help_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id in ["radius-help-button", "segments-help-button"] and not is_open:
                return True
            elif button_id == "close-help-modal" and is_open:
                return False
            return is_open
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
        # Use values from YAML configuration
        config = get_pseudo_dome_config()
        
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
        # Use values from YAML configuration
        config = get_pseudo_dome_config()
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
        # Use values from YAML configuration
        config = get_pseudo_dome_config()
        if n_clicks == 0:
            raise PreventUpdate
        
        svg_string = create_svg(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width)
        return dict(content=svg_string, filename="pseudo_dome_pattern.svg")


def register_barrel_vault_callbacks(app):
    # Help modal callbacks
    @app.callback(
        Output("barrel-help-modal", "is_open"),
        [Input("barrel-radius-help-button", "n_clicks"), 
         Input("barrel-segments-help-button", "n_clicks"),
         Input("barrel-tiles-help-button", "n_clicks"),
         Input("barrel-height-help-button", "n_clicks"),
         Input("barrel-omega-help-button", "n_clicks"),
         Input("barrel-close-help-modal", "n_clicks")],
        [State("barrel-help-modal", "is_open")],
    )
    def toggle_barrel_help_modal(radius_help_clicks, segments_help_clicks, tiles_help_clicks, 
                               height_help_clicks, omega_help_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            help_buttons = [
                "barrel-radius-help-button", 
                "barrel-segments-help-button",
                "barrel-tiles-help-button",
                "barrel-height-help-button",
                "barrel-omega-help-button"
            ]
            if button_id in help_buttons and not is_open:
                return True
            elif button_id == "barrel-close-help-modal" and is_open:
                return False
            return is_open
            
    # SVG Export callback
    @app.callback(
        Output("barrel-download-svg", "data"),
        [Input("barrel-export-button", "n_clicks")],
        [State('barrel-radius-input', 'value'),
        State('barrel-segments-input', 'value'),
        State('barrel-tiles-input', 'value'),
        State('barrel-omega-input', 'value'),
        State('barrel-height-input', 'value'),
        State('barrel-fold-color-1-input', 'value'),
        State('barrel-fold-color-2-input', 'value'),
        State('barrel-connection-color-input', 'value'),
        State('barrel-fold-width-input', 'value'),
        State('barrel-connection-width-input', 'value')],
        prevent_initial_call=True
    )
    def export_barrel_vault_svg(n_clicks, r, n, m, omega, h, fold_color_1, fold_color_2, connecting_color, mv_width, connecting_width):
        # Use values from YAML configuration
        config = get_barrel_vault_config()
        if n_clicks == 0:
            raise PreventUpdate
        
        svg_string = create_barrel_vault_svg(r, n, m, omega, h, fold_color_1, fold_color_2, connecting_color, mv_width, connecting_width)
        return dict(content=svg_string, filename="barrel_vault_pattern.svg")
        
    # DXF Export callback
    @app.callback(
        Output("barrel-download-dxf", "data"),
        [Input("barrel-export-dxf-button", "n_clicks")],
        [State('barrel-radius-input', 'value'),
        State('barrel-segments-input', 'value'),
        State('barrel-tiles-input', 'value'),
        State('barrel-omega-input', 'value'),
        State('barrel-height-input', 'value'),
        State('barrel-fold-color-1-input', 'value'),
        State('barrel-fold-color-2-input', 'value'),
        State('barrel-connection-color-input', 'value'),
        State('barrel-fold-width-input', 'value'),
        State('barrel-connection-width-input', 'value')],
        prevent_initial_call=True
    )
    def export_barrel_vault_dxf(n_clicks, r, n, m, omega, h, fold_color_1, fold_color_2, connecting_color, mv_width, connecting_width):
        # Use values from YAML configuration
        config = get_barrel_vault_config()
        if n_clicks == 0:
            raise PreventUpdate
        
        dxf_base64 = create_barrel_vault_dxf(r, n, m, omega, h, fold_color_1, fold_color_2, connecting_color, mv_width, connecting_width)
        return dict(content=dxf_base64, filename="barrel_vault_pattern.dxf", type="application/dxf", base64=True)
    @app.callback(
        [Output('barrel-pattern-plot', 'figure'),
        Output('barrel-parameter-display', 'children'),
        Output('barrel-height-label', 'children'),
        Output('barrel-height-input', 'value')], 
        [Input('barrel-radius-input', 'value'),
        Input('barrel-segments-input', 'value'),
        Input('barrel-tiles-input', 'value'),
        Input('barrel-omega-input', 'value'),
        Input('barrel-height-input', 'value')]
    )
    def update_barrel_vault_pattern(r, n, m, omega, h):
        # Calculate parameters
        theta = calculate_segment_angle(omega, n)
        s = calculate_segment_length(r, theta)
        alpha = calculate_folding_angle(theta)
        h_max = calculate_height(s, alpha)
        
        # Clamp height value between 0 and h_max
        h_clamped = np.clip(h, 0, h_max)
        
        # Update the height label
        barrel_height_label = f"Unit cell height (h) [h_max={h_max:.3f}]:"
        
        total_width = n * s
        total_height = 2 * h_clamped
        
        # Generate pattern
        traces = generate_barrel_vault_pattern(r, n, m, omega, h_clamped)
        
        # Format parameters display
        parameters_text = format_parameters(r, n, m, omega, theta, s, alpha, h_max, h_clamped, total_width, total_height)
        
        layout = go.Layout(
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                range=[-h_clamped, total_width + h_clamped]
            ),
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                range=[-total_height/2 - h_clamped/2, total_height/2 + h_clamped]
            ),
            showlegend=False
        )
        
        return {'data': traces, 'layout': layout}, parameters_text, barrel_height_label, h_clamped

   
def register_callbacks(app):
    register_pseudo_dome_callbacks(app)
    register_barrel_vault_callbacks(app)