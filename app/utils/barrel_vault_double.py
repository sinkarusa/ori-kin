import numpy as np
import plotly.graph_objs as go

from .calculations import (
    calculate_height, calculate_segment_length, calculate_alpha1_angle,
    calculate_alpha2_angle, calculate_beta_angle,
)
from .config_loader import get_double_barrel_vault_config
from .common_utils import remove_duplicate_traces, ROUNDING_DECIMAL


def generate_double_barrel_vault_pattern(r, n, m, omega, a, fold_color_1=None,
                                         fold_color_2=None, connecting_color=None,
                                         mv_width=None, connecting_width=None):
    """Return a double-centered vault pattern, with n segments per arc.

    The symmetric pointed arch determines its own arc angle acos(a/(2r)).
    omega is retained for compatibility with the shared UI and export API,
    but is not an independent parameter of this geometry (thesis section 3.2).
    m retains the existing convention of 2*m-1 two-row cells.
    """
    if not (r > 0 and 0 <= a < 2*r):
        raise ValueError('Double-centered vault requires r > 0 and 0 <= a < 2r')
    if int(n) != n or n < 2 or int(m) != m or m < 1:
        raise ValueError('n must be an integer >= 2 and m a positive integer')
    n, m = int(n), int(m)
    theta = np.degrees(np.arccos(a / (2*r))) / n
    s = calculate_segment_length(r, theta)
    alpha1 = calculate_alpha1_angle(a, r, n)
    beta = calculate_beta_angle(a, r, n)
    alpha2 = calculate_alpha2_angle(beta)
    h = min(calculate_height(s, alpha1), calculate_height(s, alpha2))
    cell, hl_pos, total_length = generate_double_barrel_vault_pattern_unit_cell(
        s, n, h, alpha1, alpha2, beta, a, fold_color_1, fold_color_2,
        connecting_color, mv_width, connecting_width)
    traces = list(cell)
    for i in range(1, m):
        for trace in cell:
            for direction in (1, -1):
                traces.append(go.Scatter(x=trace.x, y=np.asarray(trace.y) + direction*4*h*i,
                                         mode=trace.mode, line=trace.line))
    traces = remove_duplicate_traces(traces, ROUNDING_DECIMAL)
    bottom, top = hl_pos[0]*(2*m-1), hl_pos[-1]*(2*m-1)
    traces = [t for t in traces if not (
        t.y[0] == t.y[-1] and any(np.isclose(t.y[0], y, rtol=0, atol=10**-ROUNDING_DECIMAL)
                                  for y in (bottom, top)))]
    config = get_double_barrel_vault_config()
    width = mv_width or config['line_widths']['fold_width']
    for y in (bottom, top):
        traces.append(go.Scatter(x=[0, total_length], y=[y, y], mode='lines',
                                 line=dict(color='black', width=width, dash='solid')))
    return traces


def generate_double_barrel_vault_pattern_unit_cell(s, n, h, alpha1, alpha2, beta, a,
                                                    fold_color_1=None, fold_color_2=None,
                                                    connecting_color=None, mv_width=None,
                                                    connecting_width=None):
    """Draw two mirrored rows. The unique apex crease is at x=n*s.

    Every segment junction has one diagonal, with alpha2 only at the apex.
    Horizontal mountain and valley intervals alternate between those diagonals.
    """
    config = get_double_barrel_vault_config()
    mountain = fold_color_1 or config['colors']['fold_color_1']
    valley = fold_color_2 or config['colors']['fold_color_2']
    edge = connecting_color or config['colors']['connecting_color']
    width = mv_width or config['line_widths']['fold_width']
    edge_width = connecting_width or config['line_widths']['connecting_width']
    edge_style = config['line_styles']['connecting_line_style']
    total = 2*n*s
    traces = []
    def line(x1, y1, x2, y2, color, line_width=width, dash='solid'):
        if np.hypot(x2-x1, y2-y1) > 1e-12:
            traces.append(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines',
                                     line=dict(color=color, width=line_width, dash=dash)))
    for direction in (1, -1):
        outer = direction*2*h
        endpoints = {0: [0.0], outer: [0.0]}
        for k in range(1, 2*n):
            angle = alpha2 if k == n else alpha1
            dx = 2*h / np.tan(np.radians(angle))
            left, right = k*s - dx/2, k*s + dx/2
            y1, y2 = (0, outer) if k % 2 else (outer, 0)
            line(left, y1, right, y2, mountain)
            endpoints[y1].append(left)
            endpoints[y2].append(right)
        for y, xs in endpoints.items():
            xs.append(total)
            for i, (x1, x2) in enumerate(zip(xs, xs[1:])):
                is_mountain = (i % 2 == 0) if y == 0 else (i % 2 == 1)
                line(x1, y, x2, y, mountain if is_mountain else valley)
    for x in (0, total):
        line(x, -2*h, x, 2*h, edge, edge_width, edge_style)
    return remove_duplicate_traces(traces, ROUNDING_DECIMAL), [-2*h, 0, 2*h], total
