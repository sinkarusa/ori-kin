
import dash
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Add this line
# Get Plotly's Set1 colors
set1_colors = px.colors.qualitative.Set1
additional_colors = ['red', 'black', 'blue', 'green']
all_colors = set1_colors + additional_colors

# Create color options for dropdowns
color_options = [{'label': f'Color {i+1}', 'value': color} for i, color in enumerate(set1_colors)] + \
                [{'label': color.capitalize(), 'value': color} for color in additional_colors]
# Define the app layout with new input fields for colors and line widths
app.layout = html.Div([
    html.H1("Pseudo-Dome Pattern Generator with Parameters"),
    html.Div([
        html.Div([
            html.Label("Radius (r):"),
            dcc.Input(id='radius-input', type='number', value=5, min=1, step=0.1),
            html.Label("Number of segments (n):"),
            dcc.Input(id='segments-input', type='number', value=5, min=3, step=1),
            html.Label("Mountain fold color:"),
            dcc.Dropdown(id='mountain-color-input', options=color_options, value='red', clearable=False),
            html.Label("Valley fold color:"),
            dcc.Dropdown(id='valley-color-input', options=color_options, value='blue', clearable=False),
            html.Label("Radial line color:"),
            dcc.Dropdown(id='radial-color-input', options=color_options, value='black', clearable=False),
            html.Label("Mountain/Valley line width:"),
            dcc.Input(id='mv-width-input', type='number', value=2, min=1, step=1),
            html.Label("Radial line width:"),
            dcc.Input(id='radial-width-input', type='number', value=1, min=1, step=1),
            html.Button("Export SVG", id="export-button", n_clicks=0),
            dcc.Download(id="download-svg")
        ]),
        html.Div([
            dcc.Graph(id='pattern-plot')
        ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            html.H3("Calculated Parameters:"),
            html.Pre(id='parameter-display')
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '20px'})
    ])
])


def calculate_parameters(r, n):
    theta1 = np.radians(180 / (n * (n + 1)))
    theta_l = (np.pi / n) - theta1
    CD = (theta_l - theta1) / (n - 1)
    
    thetas = [theta1 + i * CD for i in range(n)]
    s = [2 * r * np.sin(theta / 2) for theta in thetas]
    A = [np.pi/2 - theta/2 for theta in thetas]
    beta = [A[i] + A[i+1] for i in range(n-1)]
    a = [2 * r * np.cos((np.pi - (thetas[i] + thetas[i+1])) / 2) for i in range(n-1)]
    
    alpha = []
    for i in range(0, n-1):
        alpha_i1 = np.arcsin(np.sin(beta[i]) * s[i+1] / a[i])
        alpha_i2 = np.arcsin(np.sin(beta[i]) * s[i] / a[i])
        alpha.append((alpha_i1, alpha_i2))
    
    # Calculate heights (h)
    h = [s[0] * np.sin(alpha[0][0])]  # h1 uses alpha11
    h.extend([s[i] * np.sin(alpha[i][0]) for i in range(1, n-1)])

    # calculate last parameters that are special
    alpha_l1 = np.pi - (beta[-1] + alpha[-2][1])
    alpha_l2 = np.pi/2 - alpha_l1

    hl = s[-1]*np.sin(alpha_l1)
    alpha.append((alpha_l1,alpha_l2))
    
    h.append(hl)
    
    # Calculate number of radial segments
    num_radial_segments = int(round(360 / (2 * np.degrees(alpha[0][0]))))
    
    return thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha[0][0], num_radial_segments

def generate_pattern(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width):
    """
    Generate the pattern for the pseudo-dome.
    
    Args:
    r (float): Radius of the dome
    n (int): Number of segments
    mountain_color (str): Color for mountain folds
    valley_color (str): Color for valley folds
    radial_color (str): Color for radial lines
    mv_width (float): Line width for mountain and valley folds
    radial_width (float): Line width for radial lines
    
    Returns:
    list: List of Plotly scatter traces representing the pattern
    """
    thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, num_radial_segments = calculate_parameters(r, n)
    
    traces = []
    
    def generate_half_pattern(inverse=False):
        current_x, current_y = 0, 0
        current_angle = 0
        points = [(current_x, current_y)]
        
        for i in range(len(s)):
            # Calculate end point of current segment
            angle_factor = -1 if inverse else 1
            next_x = current_x + s[i] * np.cos(angle_factor * current_angle)
            next_y = current_y + s[i] * np.sin(angle_factor * current_angle)
            
            # Draw the line
            color = valley_color if inverse else mountain_color
            traces.append(go.Scatter(x=[current_x, next_x], y=[current_y, next_y],
                                     mode='lines', line=dict(color=color, width=mv_width)))
            
            current_x, current_y = next_x, next_y
            points.append((current_x, current_y))
            
            # Update angle for next segment
            if i < len(s) - 1:
                if i == 0:
                    current_angle += np.pi - beta[i]
                elif i % 2 == 1:
                    current_angle -= np.pi - beta[i]
                else:
                    current_angle += np.pi - beta[i]
        
        # Add last segment with corrected angle calculation
        if inverse:
            if i % 2 == 1:
                current_angle += np.pi + alpha[-1][1]
            else:
                current_angle -= np.pi + alpha[-1][1]
            next_x = current_x + h[-1] * np.cos(-current_angle)
            next_y = current_y + h[-1] * np.sin(-current_angle)
        else:
            if i % 2 == 1:
                current_angle -= np.pi - alpha[-1][1]
            else:
                current_angle += np.pi - alpha[-1][1]
            next_x = current_x + h[-1] * np.cos(current_angle)
            next_y = current_y + h[-1] * np.sin(current_angle)
        
        points.append((next_x, next_y))
        traces.append(go.Scatter(x=[current_x, next_x], y=[current_y, next_y],
                                 mode='lines', line=dict(color=color, width=mv_width)))
        
        # Generate radial lines
        for i in range(1, len(points)):
            traces.append(go.Scatter(x=[0, points[i][0]], y=[0, points[i][1]],
                                     mode='lines', line=dict(color=radial_color, dash='dash', width=radial_width)))
    
    # Generate both halves of the pattern
    generate_half_pattern()
    generate_half_pattern(inverse=True)
    
    # Generate full radial pattern
    full_traces = traces.copy()
    for i in range(1, num_radial_segments):
        rotation = i * 2 * np.pi / num_radial_segments
        rot_matrix = np.array([[np.cos(rotation), -np.sin(rotation)],
                               [np.sin(rotation), np.cos(rotation)]])
        
        for trace in traces:
            x, y = trace['x'], trace['y']
            rotated_points = np.dot(rot_matrix, [x, y])
            full_traces.append(go.Scatter(x=rotated_points[0], y=rotated_points[1], mode='lines', 
                                          line=dict(color=trace['line']['color'], dash=trace['line']['dash'],
                                                    width=trace['line']['width'])))
    
    return full_traces

@app.callback(
    [Output('pattern-plot', 'figure'),
     Output('parameter-display', 'children')],
    [Input('radius-input', 'value'),
     Input('segments-input', 'value'),
     Input('mountain-color-input', 'value'),
     Input('valley-color-input', 'value'),
     Input('radial-color-input', 'value'),
     Input('mv-width-input', 'value'),
     Input('radial-width-input', 'value')]
)

def update_pattern(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width):
    """
    Callback function to update the pattern plot and parameter display.
    
    Args:
    r (float): Radius of the dome
    n (int): Number of segments
    mountain_color (str): Color for mountain folds
    valley_color (str): Color for valley folds
    radial_color (str): Color for radial lines
    mv_width (float): Line width for mountain and valley folds
    radial_width (float): Line width for radial lines
    
    Returns:
    tuple: (Plotly figure, Parameter display string)
    """
    if r is None or n is None:
        return go.Figure(), "Please enter valid values for r and n."

    thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, num_radial_segments = calculate_parameters(r, n)
    traces = generate_pattern(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width)

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

    param_display = f"""
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
    {', '.join([f'({np.degrees(a1):.2f}°, {np.degrees(a2):.2f}°)' for a1, a2 in alpha])}

    Heights (hi):
    {', '.join([f'{height:.2f}' for height in h])}
    """

    return figure, param_display

def create_svg(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width):
    traces = generate_pattern(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width)
    
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800px" height="800px" viewBox="-400 -400 800 800">',
    ]
    
    for trace in traces:
        x, y = trace['x'], trace['y']
        color = trace['line']['color']
        width = trace['line']['width']
        dash = trace['line']['dash']
        
        if len(x) == 2 and all(coord is not None for coord in x + y):
            x1, y1, x2, y2 = float(x[0]), -float(y[0]), float(x[1]), -float(y[1])
            stroke_dasharray = '5,5' if dash == 'dash' else 'none'
            line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{stroke_dasharray}" />'
            svg_lines.append(line)
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

@app.callback(
    Output("download-svg", "data"),
    Input("export-button", "n_clicks"),
    [State('radius-input', 'value'),
     State('segments-input', 'value'),
     State('mountain-color-input', 'value'),
     State('valley-color-input', 'value'),
     State('radial-color-input', 'value'),
     State('mv-width-input', 'value'),
     State('radial-width-input', 'value')],
    prevent_initial_call=True
)
def export_svg(n_clicks, r, n, mountain_color, valley_color, radial_color, mv_width, radial_width):
    if n_clicks == 0:
        raise PreventUpdate
    
    svg_string = create_svg(r, n, mountain_color, valley_color, radial_color, mv_width, radial_width)
    return dict(content=svg_string, filename="pseudo_dome_pattern.svg")

if __name__ == '__main__':
    app.run_server(debug=True)