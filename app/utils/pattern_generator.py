import numpy as np
import plotly.graph_objs as go

from .calculations import calculate_parameters


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
    # print(first_and_last_markers)
    return full_traces
