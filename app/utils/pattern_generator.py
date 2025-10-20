import numpy as np
import plotly.graph_objs as go

from .calculations import calculate_parameters
from .config_loader import get_pseudo_dome_config

rounding_decimal = 4

def calculate_slope(x1, y1, x2, y2):
    '''Calc slop, return Inf if horizontal'''
    if x2 - x1 == 0:
        return float('inf')  
    else:
        return (y2 - y1) / (x2 - x1)

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
        points = []
        starts_of_radial_segments = []
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
            
            if (i==0) & (current_angle==0):
                starts_of_radial_segments.append((next_x, next_y))
            
            traces.append(go.Scatter(x=[current_x, next_x], y=[current_y, next_y],
                                     mode='lines', line=dict(color=color, width=mv_width)))
            
            current_x, current_y = next_x, next_y
            
            # Update angle for next segment
            if i < len(s) - 1:
                if i == 0:
                    current_angle += np.pi - beta[i]
                elif i % 2 == 1:
                    current_angle -= np.pi - beta[i]
                else:
                    current_angle += np.pi - beta[i]
        points.append((current_x, current_y))
        starts_of_radial_segments.append((0, 0))
        if (n%2==0):
            starts_of_radial_segments = starts_of_radial_segments[::-1]
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
        
        for i in range(0, len(points)):
            # Apply line style based on configuration
            line_dash = None
            if radial_line_style in ('dash', 'dot', 'dashdot'):
                line_dash = radial_line_style
                
            traces.append(go.Scatter(x=[starts_of_radial_segments[i][0], points[i][0]], y=[starts_of_radial_segments[i][1], points[i][1]],
                                   mode='lines', line=dict(color=radial_color, width=radial_width, dash=line_dash)))

    
    # Generate both halves of the pattern
    generate_half_pattern()
    generate_half_pattern(inverse=True)

    # Remove duplicate traces
    unique_traces = []
    unique_coords = set()
    for i, trace in enumerate(traces):
        trace_coords = (np.round(trace['x'][0], rounding_decimal),
                        np.round(trace['y'][0], rounding_decimal),
                        np.round(trace['x'][-1], rounding_decimal),
                        np.round(trace['y'][-1], rounding_decimal))
        if trace_coords not in unique_coords:
            unique_coords.add(trace_coords)
            unique_traces.append(trace)
    traces = unique_traces
    # Generate full radial pattern
    full_traces = traces.copy()
    
    # import pdb; pdb.set_trace()
    for i in range(1, int(num_radial_segments/2)):
        rotation = i * 2*alpha[0][0]
        rot_matrix = np.array([[np.cos(rotation), -np.sin(rotation)],
                               [np.sin(rotation), np.cos(rotation)]])
        

        for trace in traces:
            x, y = np.array(trace['x']), np.array(trace['y'])
            rotated_points = np.dot(rot_matrix, [x, y])
            full_traces.append(go.Scatter(x=rotated_points[0], y=rotated_points[1], mode=trace['mode'],
                                        line=trace['line'] if 'line' in trace else None,
                                        marker=trace['marker'] if 'marker' in trace else None))

    # Remove duplicate traces
    unique_traces = []
    unique_coords = set()
    for i, trace in enumerate(full_traces):
        trace_coords = (np.round(trace['x'][0], rounding_decimal),
                        np.round(trace['y'][0], rounding_decimal),
                        np.round(trace['x'][-1], rounding_decimal),
                        np.round(trace['y'][-1], rounding_decimal))
        if trace_coords not in unique_coords:
            unique_coords.add(trace_coords)
            unique_traces.append(trace)
    full_traces = unique_traces
    # add a cut line to the end
    # find the trace with ending point closest to positive x axis
    closest_trace = None
    max_x = -float('inf')
    
    # last cut line should go from center to max_x, always
    for trace in full_traces:
        # Check if this trace's endpoint has a larger x value
        if len(trace['x']) > 1 and trace['x'][-1] > max_x:
            max_x = trace['x'][-1]
    
    closest_trace = full_traces[0]
    closest_trace['x'] = [closest_trace['x'][0], max_x]
    # reverse order of traces
    full_traces.reverse()
    
    # Only add the cut line if we found a valid trace
    if closest_trace is not None:
        # cutline coordinates
        cutline_xpositions = (0, closest_trace['x'][-1])
        cutline_ypositions = (0, closest_trace['y'][-1])
        cutline_slope = np.round(calculate_slope(cutline_xpositions[0], cutline_ypositions[0], cutline_xpositions[1], cutline_ypositions[1]), rounding_decimal)

        # find and remove trace that has the same endpoints as the cutline & is parallel to it
        for i, trace in enumerate(full_traces):
            trace_slope = np.round(calculate_slope(trace['x'][0], trace['y'][0], trace['x'][1], trace['y'][1]), rounding_decimal)
            if (np.round(trace['x'][1], rounding_decimal) == np.round(cutline_xpositions[1], rounding_decimal)) and\
               (np.round(trace['y'][1], rounding_decimal) == np.round(cutline_ypositions[1], rounding_decimal)) and\
               (trace_slope ==cutline_slope):
                full_traces.pop(i)
                # break
        # Add a cut line from origin to the endpoint of the trace closest to positive x-axis
        full_traces.append(go.Scatter(
            x=cutline_xpositions, 
            y=cutline_ypositions, 
            mode='lines', 
            line=dict(color=fold_color_1, width=mv_width)
        ))

    return full_traces
