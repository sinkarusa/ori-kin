import numpy as np
import plotly.graph_objs as go

from .calculations import (
    calculate_folding_angle,
    calculate_height,
    calculate_segment_angle,
    calculate_segment_length,
    calculate_alpha1_angle,
    calculate_alpha2_angle,
    calculate_beta_angle
)
from .config_loader import get_double_barrel_vault_config
from .common_utils import remove_duplicate_traces, ROUNDING_DECIMAL

rounding_decimal = ROUNDING_DECIMAL

def generate_double_barrel_vault_pattern(r, n, m, omega, a, fold_color_1=None, fold_color_2=None,
                               connecting_color=None, mv_width=None, connecting_width=None):
    """
    Generate double barrel vault pattern.

    Args:
        r: Radius
        n: Number of segments
        m: Number of tiles
        omega: Central angle
        a: Distance between barrel vault centers
        fold_color_1: Mountain fold color
        fold_color_2: Valley fold color
        connecting_color: Connecting line color
        mv_width: Mountain/valley fold width
        connecting_width: Connecting line width

    Returns:
        List of Plotly scatter traces
    """
    # Load configuration from YAML file
    config = get_double_barrel_vault_config()

    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    connecting_color = connecting_color or config['colors']['connecting_color']
    mv_width = mv_width or config['line_widths']['fold_width']
    connecting_width = connecting_width or config['line_widths']['connecting_width']
    connecting_line_style = config['line_styles']['connecting_line_style']

    # Calculate basic parameters
    theta = calculate_segment_angle(omega, n)
    s = calculate_segment_length(r, theta)
    alpha1 = calculate_alpha1_angle(a,r,n)
    beta = calculate_beta_angle(a,r,n)
    alpha2 = calculate_alpha2_angle(beta)
    h = calculate_height(s, alpha1)  # Calculate h from geometry
    
    unit_cell_traces, hl_pos, total_length = generate_double_barrel_vault_pattern_unit_cell(s, n, h, alpha1,alpha2,beta, a,
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
        # Remove duplicate traces
    full_traces = remove_duplicate_traces(full_traces, rounding_decimal)

    # change to color of top and bottom most horizontal traces
    y_bottom = hl_pos[0]*(2*m-1)
    y_top = hl_pos[-1]*(2*m-1)

    ## remove all traces on top and bottom
    traces_final = []
    for i, trace in enumerate(full_traces):
        if trace['y'][0] == trace['y'][-1]:
            # if horizontal
            if not ((np.round(trace['y'][0], rounding_decimal) == np.round(y_bottom, rounding_decimal))\
                or (np.round(trace['y'][0], rounding_decimal) == np.round(y_top, rounding_decimal))):
                traces_final.append(trace)
        else:
            traces_final.append(trace)
    # ## add new traces to top on bottom that are black
    for hlp in [y_bottom, y_top]:
        traces_final.append(go.Scatter(
            x=[0, total_length],
            y=[hlp,hlp],
            mode='lines',
            line=dict(color='black', width=mv_width, dash='solid')
        ))
    return traces_final

def generate_double_barrel_vault_pattern_unit_cell(s, n, h, alpha1, alpha2,beta, a, fold_color_1=None, fold_color_2=None,
                               connecting_color=None, mv_width=None, connecting_width=None):
    # Load configuration from YAML file
    config = get_double_barrel_vault_config()
    
    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    connecting_color = connecting_color or config['colors']['connecting_color']
    mv_width = mv_width or config['line_widths']['fold_width']
    connecting_width = connecting_width or config['line_widths']['connecting_width']
    connecting_line_style = config['line_styles']['connecting_line_style']
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
    s_angled_alpha1 = np.abs(2*h/np.tan(np.pi*alpha1/180))
    s_angled_alpha2 = np.abs(2*h/np.tan(np.pi*alpha2/180))
    # Generate horizontal segment at the begining
    current_x = 0
    current_y = 0
    first_flat_segment_length =s-s_angled_alpha1/2
    next_x = current_x + first_flat_segment_length
    next_y = current_y
    # Horizontal segment
    # color = fold_color_1 if i % 2 == 0 else fold_color_2
    traces.append(go.Scatter(
        x=[current_x, next_x],
        y=[current_y, next_y],
        mode='lines',
        line=dict(color=fold_color_1, width=mv_width)
    ))

    # valley folds start and end points
    valley_fold_traces = []
    valley_fold_traces.append([(next_x, next_y)])

    n_reps = int(np.floor(n/2)) if n%2 else int(n/2)-1
    current_x_sym_org = next_x
    current_y_sym_org = next_y

    valley_fold_color = fold_color_2
    for j in range(2): 
        # for +y and -y direction
        y_dir = 1 if j==0 else -1
        current_x = current_x_sym_org
        current_y = current_y_sym_org
        # center valley fold 
        
        upper_and_lower_valley_fold_start = [0, y_dir*2*h]
        for i in range(n_reps):
            if (i+1) % 2:
                next_x = current_x + s_angled_alpha1
                next_y = current_y + y_dir*2*h
                center_valley_fold_start = [current_x, current_y]
                # Upper diagonal
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1, width=mv_width)
                ))
                current_x = next_x
                current_y = next_y

                # add upper valley fold 
                traces.append(go.Scatter(
                    x=[upper_and_lower_valley_fold_start[0], next_x],
                    y=[upper_and_lower_valley_fold_start[1], upper_and_lower_valley_fold_start[1]],
                    mode='lines',
                    line=dict(color=valley_fold_color, width=mv_width, dash='solid')
                ))
                
                next_x = current_x + s - s_angled_alpha1
                next_y = current_y
                if next_x>current_x:
                    # trapezoid straigth section
                    traces.append(go.Scatter(
                        x=[current_x, next_x],
                        y=[current_y, next_y],
                        mode='lines',
                        line=dict(color=fold_color_1, width=mv_width)
                    ))
                upper_and_lower_valley_fold_start = [next_x, next_y]
            else: 
                next_x = current_x + (s - s_angled_alpha2)/2
                next_y = current_y
                # trapezoid straigth section
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1, width=mv_width)
                ))

                current_x = next_x
                current_y = next_y
                center_valley_fold_start = [current_x, current_y]

                next_x = current_x + s_angled_alpha2
                next_y = current_y + y_dir*2*h
                # Upper diagonal
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1, width=mv_width)
                ))
                current_x = next_x
                current_y = next_y

                # add upper valley fold 
                traces.append(go.Scatter(
                    x=[upper_and_lower_valley_fold_start[0], next_x],
                    y=[upper_and_lower_valley_fold_start[1], upper_and_lower_valley_fold_start[1]],
                    mode='lines',
                    line=dict(color=valley_fold_color, width=mv_width, dash='solid')
                ))
                
                next_x = current_x + (s - s_angled_alpha2)/2
                next_y = current_y
                # trapezoid straigth section
                traces.append(go.Scatter(
                    x=[current_x, next_x],
                    y=[current_y, next_y],
                    mode='lines',
                    line=dict(color=fold_color_1, width=mv_width)
                ))
                upper_and_lower_valley_fold_start = [next_x, next_y]
            
            #lower diagonal
            current_x = next_x
            current_y = next_y
            next_x = current_x + s_angled_alpha1
            next_y = current_y - y_dir*2*h
            center_valley_fold_end = (next_x, next_y)
            # Lower diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1, width=mv_width)
            ))
            current_x = next_x
            current_y = next_y
            
            # add center valley fold
            traces.append(go.Scatter(
                x=[center_valley_fold_start[0], center_valley_fold_end[0]],
                y=[center_valley_fold_start[1], center_valley_fold_end[1]],
                mode='lines',
                line=dict(color=valley_fold_color, width=mv_width, dash='solid')
            ))
            next_x = current_x + s - s_angled_alpha1
            next_y = current_y

            if (n%2==1) & (i==n_reps-1):
                next_x = current_x + first_flat_segment_length

            
            # if next_x>current_x:
            # trapezoid straigth section
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1, width=mv_width)
            ))
            current_x = next_x
            current_y = next_y

            
        if n%2==0:
            # then we do one diagonal step only
            center_valley_fold_start[0] = current_x
            next_x = current_x + s_angled_alpha1
            next_y = current_y + y_dir*2*h
            # Upper diagonal
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1, width=mv_width)
            ))

            
            current_x = next_x
            current_y = next_y
            
            next_x = current_x + s-s_angled_alpha1/2
            next_y = current_y
            
            # if next_x>current_x:
            # trapezoid straigth section
            traces.append(go.Scatter(
                x=[current_x, next_x],
                y=[current_y, next_y],
                mode='lines',
                line=dict(color=fold_color_1, width=mv_width)
            ))
            if (i==n_reps-1):
                traces.append(go.Scatter(
                    x=[center_valley_fold_start[0], next_x],
                    y=[center_valley_fold_start[1], center_valley_fold_end[1]],
                    mode='lines',
                    line=dict(color=valley_fold_color, width=mv_width, dash='solid')
                ))
        
            # current_x = next_x
            # current_y = next_y

        # else:
            # add center valley fold
            # center_valley_fold_start[0] = current_x
        # if n % 2:
        traces.append(go.Scatter(
            x=[upper_and_lower_valley_fold_start[0], current_x],
            y=[upper_and_lower_valley_fold_start[1], upper_and_lower_valley_fold_start[1]],
            mode='lines',
            line=dict(color=valley_fold_color, width=mv_width, dash='solid')
        ))
            

    
    # horizontal lines i.e. Valley folds
    hl_pos = [-2*h,0,2*h]
    total_length = n*s
    # for hlp in hl_pos:
    #     traces.append(go.Scatter(
    #         x=[0, total_length],
    #         y=[hlp,hlp],
    #         mode='lines',
    #         line=dict(color=fold_color_2, width=mv_width, dash='dash')
    #     ))
   
    # vertical lines
    vl_pos = [0,total_length]
    for vlp in vl_pos:
        traces.append(go.Scatter(
            x=[vlp,vlp],
            y=[np.min(hl_pos),np.max(hl_pos)],
            mode='lines',
            line=dict(color=connecting_color, width=connecting_width, dash=connecting_line_style)
        ))
    
    # Remove duplicate traces
    traces = remove_duplicate_traces(traces, rounding_decimal)
    return traces, hl_pos, total_length