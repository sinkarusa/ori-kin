import numpy as np
import plotly.graph_objs as go

from .calculations import (
    calculate_folding_angle,
    calculate_height,
    calculate_segment_angle,
    calculate_segment_length,
)


def generate_barrel_vault_pattern(r, n, m, omega, h, fold_color_1='red', fold_color_2='blue', 
                               connecting_color='gray', mv_width=2, connecting_width=1):
    
    # Calculate basic parameters
    theta = calculate_segment_angle(omega, n)
    s = calculate_segment_length(r, theta)
    alpha = calculate_folding_angle(theta)
    h_max = calculate_height(s, alpha)
    h = np.clip(h,0,h_max)
    
    unit_cell_traces = generate_barrel_vault_pattern_unit_cell(s,n,h, alpha,
                        fold_color_1=fold_color_1, fold_color_2=fold_color_2, 
                        connecting_color=connecting_color, mv_width=mv_width, 
                        connecting_width=connecting_width)
    
    full_traces = [t for t in unit_cell_traces]
    for i in range(1, m):
        for trace in unit_cell_traces:
            x, y = np.array(trace['x']), np.array(trace['y'])
            y_translated = y+4*h*i
            full_traces.append(
                go.Scatter(x=x, y=y_translated,
                           mode=trace['mode'],
                           line=trace['line'] if 'line' in trace else None,
                           marker=trace['marker'] if 'marker' in trace else None))
            y_translated = y-4*h*i
            full_traces.append(
                go.Scatter(x=x, y=y_translated,
                           mode=trace['mode'],
                           line=trace['line'] if 'line' in trace else None,
                           marker=trace['marker'] if 'marker' in trace else None))
    return full_traces

def generate_barrel_vault_pattern_unit_cell(s,n,h,alpha, fold_color_1='red', fold_color_2='blue', 
                               connecting_color='gray', mv_width=2, connecting_width=1):
    """
    Generate traces for the barrel vault pattern.
    
    
    omega (float): Central angle in degrees
    fold_color_1 (str): Color for mountain folds
    fold_color_2 (str): Color for valley folds
    connecting_color (str): Color for connecting lines
    mv_width (float): Line width for mountain and valley folds
    connecting_width (float): Line width for connecting lines
    
    Returns:
    list: List of Plotly scatter traces
    """

    
    traces = []
    
    s_angled = np.abs(2*h/np.tan(np.pi*alpha/180))
    # Generate horizontal segment at the begining
    current_x = 0
    current_y = 0
    next_x = current_x + s-s_angled/2
    next_y = current_y
    # Horizontal segment
    # color = fold_color_1 if i % 2 == 0 else fold_color_2
    traces.append(go.Scatter(
        x=[current_x, next_x],
        y=[current_y, next_y],
        mode='lines',
        line=dict(color='green', width=mv_width)
    ))
    
    
    n_reps = int(np.floor(n/2)) if n%2 else int(n/2)-1
    current_x_sym_org = next_x
    current_y_sym_org = next_y
    for j in range(2): 
        # for +y and -y direction
        y_dir = 1 if j==0 else -1
        current_x = current_x_sym_org
        current_y = current_y_sym_org
        for i in range(n_reps):
            next_x = current_x + s_angled
            next_y = current_y + y_dir*2*h
            # Upper diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1 if j%2 else fold_color_2, width=mv_width)
            ))
            current_x = next_x
            current_y = next_y
            
            next_x = current_x + s-s_angled
            next_y = current_y
            if next_x>current_x:
                # trapezoid straigth section
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1 if j%2 else fold_color_2, width=mv_width)
                ))
            #lower diagonal
            current_x = next_x
            current_y = next_y
            next_x = current_x + s_angled
            next_y = current_y - y_dir*2*h
            # Lower diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1 if j%2 else fold_color_2, width=mv_width)
            ))
            current_x = next_x
            current_y = next_y
            
            next_x = current_x + s-s_angled
            next_y = current_y
            if next_x>current_x:
                # trapezoid straigth section
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1 if j%2 else fold_color_2, width=mv_width)
                ))
            current_x = next_x
            current_y = next_y
        if n%2==0:
            next_x = current_x + s_angled
            next_y = current_y + y_dir*2*h
            # Upper diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1 if j%2 else fold_color_2, width=mv_width)
            ))
            current_x = next_x
            current_y = next_y
            
            next_x = current_x + s-s_angled/2
            next_y = current_y
            if next_x>current_x:
                # trapezoid straigth section
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color='green', width=mv_width)
                ))
            current_x = next_x
            current_y = next_y
    # horizontal lines
    hl_pos = [-2*h,0,2*h]
    total_length = n*s
    for hlp in hl_pos:
        traces.append(go.Scatter(
            x=[0, total_length],
            y=[hlp,hlp],
            mode='lines',
            line=dict(color=connecting_color, width=connecting_width, dash='dash')
        ))
   
    # vertical lines
    vl_pos = [0,total_length]
    for vlp in vl_pos:
        traces.append(go.Scatter(
            x=[vlp,vlp],
            y=[np.min(hl_pos),np.max(hl_pos)],
            mode='lines',
            line=dict(color=connecting_color, width=connecting_width, dash='solid')
        ))
    
    return traces