"""
Common utility functions shared across pattern generators and export functions.
"""
import numpy as np

# Default rounding precision for coordinate comparison
ROUNDING_DECIMAL = 4


def remove_duplicate_traces(traces, rounding_decimal=ROUNDING_DECIMAL):
    """
    Remove duplicate traces based on rounded endpoint coordinates.

    Two traces are considered duplicates if they have the same start and end points
    (within rounding precision), regardless of direction.

    Args:
        traces (list): List of traces (Plotly go.Scatter objects or dictionaries)
        rounding_decimal (int): Number of decimal places to round coordinates to

    Returns:
        list: List of unique traces
    """
    unique_traces = []
    unique_coords = set()

    for trace in traces:
        # Handle both go.Scatter objects and dictionaries
        if hasattr(trace, 'x') and hasattr(trace, 'y'):
            # This is a go.Scatter object
            x, y = trace.x, trace.y
        else:
            # This is a dictionary
            x, y = trace['x'], trace['y']

        # Create coordinate tuple for comparison
        trace_coords = (
            np.round(x[0], rounding_decimal),
            np.round(y[0], rounding_decimal),
            np.round(x[-1], rounding_decimal),
            np.round(y[-1], rounding_decimal)
        )

        if trace_coords not in unique_coords:
            unique_coords.add(trace_coords)
            unique_traces.append(trace)

    return unique_traces


def get_dxf_color(rgb_str):
    """
    Convert RGB color string to DXF color code.

    DXF uses standard color codes:
    - Red = 1
    - Yellow = 2
    - Green = 3
    - Cyan = 4
    - Blue = 5
    - Magenta = 6
    - White = 7
    - Black = 9

    Args:
        rgb_str (str): RGB color string like "rgb(255,0,0)" or "black"

    Returns:
        int: DXF color code
    """
    if 'rgb' in rgb_str:
        # Parse RGB values from string like "rgb(0,255,0)"
        rgb_values = rgb_str.replace('rgb(', '').replace(')', '').split(',')
        r, g, b = [int(val.strip()) for val in rgb_values]

        # Simple color mapping based on dominant channel
        if r > g and r > b: return 1  # Red
        if g > r and g > b: return 3  # Green
        if b > r and b > g: return 5  # Blue
        if r > 200 and g > 200: return 2  # Yellow
        if g > 200 and b > 200: return 4  # Cyan
        if r > 200 and b > 200: return 6  # Magenta
        return 7  # White/default
    elif rgb_str == 'black':
        return 9
    return 7  # Default to white
