from io import BytesIO

import dash
import ezdxf
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
            html.Div([
                html.Label("Radius (r):"),
                dcc.Input(id='radius-input', type='number', value=5, min=1, step=0.1)
            ], style={'margin-bottom': '10px'}),
            html.Div([
                html.Label("Number of segments (n):"),
                dcc.Input(id='segments-input', type='number', value=5, min=3, step=1)
            ], style={'margin-bottom': '10px'}),
            html.Label("Fold color 1:"),
            dcc.Dropdown(id='fold-color-1-input', options=color_options, value='red', clearable=False),
            html.Label("Fold color 2:"),
            dcc.Dropdown(id='fold-color-2-input', options=color_options, value='blue', clearable=False),
            html.Label("Radial line color:"),
            dcc.Dropdown(id='radial-color-input', options=color_options, value='black', clearable=False),
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
    num_radial_segments = int(round(360 / (2 * np.degrees(alpha[0][0]/2))))
    
    return thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha[0][0], num_radial_segments

def generate_pattern(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width):
    """
    Generate the pattern for the pseudo-dome.
    
    Args:
    r (float): Radius of the dome
    n (int): Number of segments
    fold_color_1 (str): Color for mountain folds
    fold_color_2 (str): Color for valley folds
    radial_color (str): Color for radial lines
    mv_width (float): Line width for mountain and valley folds
    radial_width (float): Line width for radial lines
    
    Returns:
    list: List of Plotly scatter traces representing the pattern
    """
    thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, num_radial_segments = calculate_parameters(r, n)
    # print(180*alpha[0][0]/np.pi)
    traces = []
    first_and_last_markers = []
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
            color = fold_color_2 if inverse else fold_color_1
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
        # Add markers for the last point of the trace
        # marker_x = next_x if i % 2 == 0 else current_x
        # marker_y = next_y if i % 2 == 0 else current_y

        # if inverse:
        #      # Add a dot at the last point of the trace
        #     traces.append(go.Scatter(x=[marker_x], y=[marker_y], mode='markers',
        #                             marker=dict(color=color, size=10, symbol='x')))
        # else:
        #     traces.append(go.Scatter(x=[marker_x], y=[marker_y], mode='markers',
        #                             marker=dict(
        #                                 size=10,
        #                                 symbol='circle',
        #                                 line=dict(color=color, width=2),  # Outline color of the marker
        #                                 color='rgba(0, 0, 0, 0)'  # Transparent fill inside the marker
        #                             )))
        # first_and_last_markers.append((marker_x,marker_y))
    
    # Generate both halves of the pattern
    generate_half_pattern()
    generate_half_pattern(inverse=True)
    
    # Generate full radial pattern
    full_traces = traces.copy()
    
    # import pdb; pdb.set_trace()
    for i in range(1, int(num_radial_segments/2)):
    # for i in range(0,1):
        rotation = i * 2*alpha[0][0]
        rot_matrix = np.array([[np.cos(rotation), -np.sin(rotation)],
                               [np.sin(rotation), np.cos(rotation)]])
        

        for trace in traces:
            x, y = np.array(trace['x']), np.array(trace['y'])
            rotated_points = np.dot(rot_matrix, [x, y])
            full_traces.append(go.Scatter(x=rotated_points[0], y=rotated_points[1], mode=trace['mode'],
                                        line=trace['line'] if 'line' in trace else None,
                                        marker=trace['marker'] if 'marker' in trace else None))

            if i == int(num_radial_segments/2)-1:
                if trace['mode'] == 'marker':
                    first_and_last_markers.append((rotated_points[x][0],rotated_points[y][0]))
    print(first_and_last_markers)
    return full_traces

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
{folding_angles}

Heights (hi):
{', '.join([f'{height:.2f}' for height in h])}
"""

    return figure, param_display

import os
import tempfile


def create_dxf(r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width):
    """
    Create DXF file with exact dimensions matching the pattern generation
    Using newer AutoCAD format for better compatibility
    """
    try:
        # Use AutoCAD 2010 format instead of R12
        doc = ezdxf.new('AC1024')  # AutoCAD 2010
        msp = doc.modelspace()

        # Set units to meters with absolute coordinates
        doc.header['$MEASUREMENT'] = 1     # Set measurement to metric
        doc.header['$INSUNITS'] = 1        # 1 = meters
        doc.header['$LUNITS'] = 2          # Scientific notation
        doc.header['$AUNITS'] = 0          # Decimal degrees
        doc.header['$UNITMODE'] = 0        # Display units as decimal
        
        # Create required linetypes
        if 'DASHED' not in doc.linetypes:
            doc.linetypes.add('DASHED', pattern='A,0.5,-0.25')

        # Get pattern using existing generate_pattern function
        traces = generate_pattern(r, n, fold_color_1, fold_color_2, radial_color, fold_width, radial_width)
        
        # Track pattern extents for verification
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # Add pattern lines using exact coordinates from generate_pattern
        for trace in traces:
            x, y = trace['x'], trace['y']
            
            if len(x) == 2 and all(coord is not None for coord in x + y):
                start = (float(x[0]), float(y[0]))
                end = (float(x[1]), float(y[1]))
                
                min_x = min(min_x, start[0], end[0])
                max_x = max(max_x, start[0], end[0])
                min_y = min(min_y, start[1], end[1])
                max_y = max(max_y, start[1], end[1])
                
                # Add lines with appropriate line type and color
                if 'dash' in trace['line'] and trace['line']['dash'] == 'dash':
                    msp.add_line(start, end, dxfattribs={
                        'linetype': 'DASHED',
                        'color': 7  # White/black
                    })
                else:
                    color = 1 if trace['line']['color'] == fold_color_1 else 5  # Red=1, Blue=5
                    msp.add_line(start, end, dxfattribs={'color': color})

        # Print exact dimensions for verification
        print(f"DXF Pattern Dimensions:")
        print(f"X extent: {min_x:.6f}m to {max_x:.6f}m (width: {(max_x - min_x):.6f}m)")
        print(f"Y extent: {min_y:.6f}m to {max_y:.6f}m (height: {(max_y - min_y):.6f}m)")
        print(f"Input radius: {r:.6f}m")
        print(f"Measured radius: {max(abs(max_x), abs(max_y)):.6f}m")
        
        # Add verification circle at exact input radius
        msp.add_circle((0, 0), r, dxfattribs={'color': 3})  # Green

        # Setup dimension style
        dimstyle = doc.dimstyles.new('METRIC')
        dimstyle.dxf.dimscale = 1.0
        dimstyle.dxf.dimexe = 0.05
        dimstyle.dxf.dimexo = 0.05
        dimstyle.dxf.dimasz = 0.1
        dimstyle.dxf.dimtxt = 0.2
        
        # Add diameter dimension
        msp.add_linear_dim(
            base=(0, min_y - 0.5),
            p1=(-max_x, 0),
            p2=(max_x, 0),
            dimstyle='METRIC',
            override={
                'dimtxt': 0.2,
                'dimclrd': 7,  # Dimension line color
                'dimclre': 7   # Extension line color
            }
        ).render()

        # Create temporary file and save
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_filename = tmp_file.name
            doc.saveas(tmp_filename)
            
            file_size = os.path.getsize(tmp_filename)
            print(f"DXF file created: {file_size} bytes")
            
            with open(tmp_filename, 'rb') as f:
                buffer = BytesIO(f.read())
            
        os.unlink(tmp_filename)
        
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"Error creating DXF: {str(e)}")
        print(f"Error details: {str(e.__class__.__name__)}")
        raise
# Add a new callback for DXF export
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


def create_svg(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width):
    traces = generate_pattern(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width)
    
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

if __name__ == '__main__':
    app.run_server(debug=True)