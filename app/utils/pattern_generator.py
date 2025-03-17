import numpy as np
import plotly.graph_objs as go

from .calculations import calculate_parameters
from .config_loader import get_pseudo_dome_config


def generate_pattern(r, n, fold_color_1=None, fold_color_2=None, radial_color=None, mv_width=None, radial_width=None):
    # Load configuration from YAML file
    config = get_pseudo_dome_config()
    
    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    radial_color = radial_color or config['colors']['radial_color']
    mv_width = mv_width or config['line_widths']['fold_width']
    radial_width = radial_width or config['line_widths']['radial_width']
    radial_line_style = config['line_styles']['radial_line_style']
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
    # first_and_last_markers = []
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
            if i > 0:
                color = fold_color_2
            else:
                color = fold_color_1
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
        # change color of last trace
        traces[-1].line.color = 'black'

        # Generate radial lines
        
        for i in range(1, len(points)):
            # Apply line style based on configuration
            line_dash = None
            if radial_line_style in ('dash', 'dot', 'dashdot'):
                line_dash = radial_line_style
                
            traces.append(go.Scatter(x=[0, points[i][0]], y=[0, points[i][1]],
                                   mode='lines', line=dict(color=radial_color, width=radial_width, dash=line_dash)))

    
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

            # if i == int(num_radial_segments/2)-1:
            #     if trace['mode'] == 'marker':
            #         first_and_last_markers.append((rotated_points[x][0],rotated_points[y][0]))
    # print(first_and_last_markers)
    # reverse order of traces
    full_traces.reverse()
    return full_traces
