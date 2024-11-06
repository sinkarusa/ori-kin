import numpy as np
import plotly.graph_objs as go

from .calculations import (
    calculate_folding_angle,
    calculate_height,
    calculate_segment_angle,
    calculate_segment_length,
)


def generate_barrel_vault_pattern(r, n, omega, fold_color_1='red', fold_color_2='blue', 
                               connecting_color='gray', mv_width=2, connecting_width=1):
    """
    Generate traces for the barrel vault pattern.
    
    Args:
    r (float): Radius
    n (int): Number of segments
    omega (float): Central angle in degrees
    fold_color_1 (str): Color for mountain folds
    fold_color_2 (str): Color for valley folds
    connecting_color (str): Color for connecting lines
    mv_width (float): Line width for mountain and valley folds
    connecting_width (float): Line width for connecting lines
    
    Returns:
    list: List of Plotly scatter traces
    """
    # Calculate basic parameters
    theta = calculate_segment_angle(omega, n)
    s = calculate_segment_length(r, theta)
    alpha = calculate_folding_angle(theta)
    h = calculate_height(s, alpha)
    
    traces = []
    # Create parameter annotations
    param_text = (
        f'Parameters:<br>'
        f'r = {r:.2f}<br>'
        f'n = {n}<br>'
        f'Ω = {omega}°<br>'
        f'θ = {theta:.2f}°<br>'
        f's = {s:.2f}<br>'
        f'α = {alpha:.2f}°<br>'
        f'h = {h:.2f}'
    )
    
    # Add parameter annotation trace
    traces.append(go.Scatter(
        x=[0],
        y=[h + h/2],  # Position above the pattern
        mode='text',
        text=[param_text],
        textposition="top left",
        textfont=dict(size=12),
        showlegend=False,
        hoverinfo='none'
    ))
    # Generate horizontal segment at the begingng
    current_x = 0
    current_y = 0
    next_x = current_x + s
    next_y = current_y
    # Horizontal segment
    # color = fold_color_1 if i % 2 == 0 else fold_color_2
    traces.append(go.Scatter(
        x=[current_x, next_x],
        y=[current_y, next_y],
        mode='lines',
        line=dict(color='black', width=mv_width)
    ))
    
    n_reps = int(n/2)+1 if n%2 else int(n/2)
    current_x_sym_org = next_x
    current_y_sym_org = next_y
    for j in range(2): 
        # for +y and -y direction
        y_dir = 1 if j==0 else -1
        current_x = current_x_sym_org
        current_y = current_y_sym_org
        for i in range(n_reps):
            next_x = current_x + s
            next_y = current_y + y_dir*h
            # Upper diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1 if (next_y-current_y) > 0 else fold_color_2, width=mv_width)
            ))
            
            current_x = next_x
            current_y = next_y
            next_x = current_x + s
            next_y = current_y - y_dir*h
            # Lower diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1 if (next_y-current_y) > 0 else fold_color_2, width=mv_width)
            ))
            
            current_x = next_x
            current_y = next_y
        
    # Upper horizontal line
    traces.append(go.Scatter(
        x=[0, n*s+1],
        y=[h, h],
        mode='lines',
        line=dict(color=connecting_color, width=connecting_width, dash='dash')
    ))
    
    # Lower horizontal line
    traces.append(go.Scatter(
        x=[0, n*s+1],
        y=[-h, -h],
        mode='lines',
        line=dict(color=connecting_color, width=connecting_width, dash='dash')
    ))
    
    # Left vertical connecting line
    traces.append(go.Scatter(
        x=[0, 0],
        y=[-h, h],
        mode='lines',
        line=dict(color=connecting_color, width=connecting_width, dash='dash')
    ))
    
    # Right vertical connecting line
    traces.append(go.Scatter(
        x=[n*s+1, n*s+1],
        y=[-h, h],
        mode='lines',
        line=dict(color=connecting_color, width=connecting_width, dash='dash')
    ))
    
    return traces