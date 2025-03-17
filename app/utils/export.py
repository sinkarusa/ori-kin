import os
import tempfile
from io import BytesIO

import ezdxf

from .pattern_generator import generate_pattern
from .config_loader import get_pseudo_dome_config


def create_dxf(r, n, fold_color_1=None, fold_color_2=None, radial_color=None, fold_width=None, radial_width=None):
    # Load configuration from YAML file
    config = get_pseudo_dome_config()
    
    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    radial_color = radial_color or config['colors']['radial_color']
    fold_width = fold_width or config['line_widths']['fold_width']
    radial_width = radial_width or config['line_widths']['radial_width']
    radial_line_style = config['line_styles']['radial_line_style']
    
    # Convert RGB color strings to DXF color codes
    # For DXF, we'll use standard colors that are closest to our RGB values
    # Red = 1, Yellow = 2, Green = 3, Cyan = 4, Blue = 5, Magenta = 6, White = 7
    def get_dxf_color(rgb_str):
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
        elif rgb_str=='black':
            return 9
        return 7  # Default to white
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
        doc.header['$INSUNITS'] = 6        # 6 = meters (1 = inches)
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
                # Apply line style based on configuration
                if trace['line']['color'] == radial_color:
                    linetype = 'CONTINUOUS'
                    if radial_line_style in ['dash', 'dot', 'dashdot']:
                        linetype = radial_line_style
                    
                    # Use the color mapping function for radial color
                    dxf_color = get_dxf_color(radial_color)
                    msp.add_line(start, end, dxfattribs={
                        'linetype': linetype,
                        'color': dxf_color,
                        'lineweight': radial_width
                    })
                else:
                    # Determine if this is fold_color_1 or fold_color_2
                    dxf_color = get_dxf_color(trace['line']['color'])
                    msp.add_line(start, end, dxfattribs={
                        'color': dxf_color,
                        'lineweight': fold_width
                    })

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

def create_svg(r, n, fold_color_1=None, fold_color_2=None, radial_color=None, mv_width=None, radial_width=None):
    # Load configuration from YAML file
    config = get_pseudo_dome_config()
    
    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    radial_color = radial_color or config['colors']['radial_color']
    mv_width = mv_width or config['line_widths']['fold_width']
    radial_width = radial_width or config['line_widths']['radial_width']
    radial_line_style = config['line_styles']['radial_line_style']
    traces = generate_pattern(r, n, fold_color_1, fold_color_2, radial_color, mv_width, radial_width)
    
    # We'll set the viewBox after calculating the actual pattern dimensions
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        # Placeholder for viewBox, will be replaced after calculating dimensions
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800px" height="800px" viewBox="0 0 0 0" preserveAspectRatio="xMidYMid meet">',
        # Add a comment about units
        '<!-- Pattern dimensions in meters -->',
    ]
    
    # Track min/max coordinates to verify viewBox
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for trace in traces:
        x, y = trace['x'], trace['y']
        color = trace['line']['color']
        width = trace['line']['width']
        dash = trace['line']['dash']
        
        if len(x) == 2 and all(coord is not None for coord in x + y):
            x1, y1, x2, y2 = float(x[0]), -float(y[0]), float(x[1]), -float(y[1])
            
            # Track pattern extents
            min_x = min(min_x, x1, x2)
            max_x = max(max_x, x1, x2)
            min_y = min(min_y, y1, y2)
            max_y = max(max_y, y1, y2)
            
            # Apply line style based on configuration
            stroke_dasharray = 'none'
            if dash == 'dash' or (color == radial_color and radial_line_style == 'dash'):
                stroke_dasharray = '5,5'
            elif dash == 'dot' or (color == radial_color and radial_line_style == 'dot'):
                stroke_dasharray = '1,3'
            elif dash == 'dashdot' or (color == radial_color and radial_line_style == 'dashdot'):
                stroke_dasharray = '5,2,1,2'
            
            # Ensure color is properly formatted
            if color.startswith('rgb'):
                # Already in correct format
                stroke_color = color
            else:
                # Default to config colors if not in RGB format
                if color == fold_color_1:
                    stroke_color = config['colors']['fold_color_1']
                elif color == fold_color_2:
                    stroke_color = config['colors']['fold_color_2']
                elif color == radial_color:
                    stroke_color = config['colors']['radial_color']
                else:
                    stroke_color = color
            
            # Scale the line width to be proportional to the pattern size
            # This ensures line widths look appropriate regardless of pattern size
            scaled_width = width * 0.01  # Scale down the line width
                    
            line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{scaled_width}" stroke-dasharray="{stroke_dasharray}" />'
            svg_lines.append(line)
    
    svg_lines.append('</svg>')
    
    # Calculate the ideal viewBox based on actual pattern dimensions
    pattern_width = max_x - min_x
    pattern_height = max_y - min_y
    
    # Add 10% padding around the pattern
    padding_x = pattern_width * 0.1
    padding_y = pattern_height * 0.1
    
    # Calculate viewBox parameters
    viewbox_x = min_x - padding_x
    viewbox_y = min_y - padding_y
    viewbox_width = pattern_width + (2 * padding_x)
    viewbox_height = pattern_height + (2 * padding_y)
    
    # Add metadata to the SVG to indicate units
    svg_lines.insert(3, f'<metadata>\n  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n    <rdf:Description>\n      <units>meters</units>\n      <radius>{r}</radius>\n      <segments>{n}</segments>\n    </rdf:Description>\n  </rdf:RDF>\n</metadata>')
    
    # Replace the placeholder viewBox with the calculated one
    viewbox_str = f'{viewbox_x} {viewbox_y} {viewbox_width} {viewbox_height}'
    svg_content = '\n'.join(svg_lines)
    svg_content = svg_content.replace('viewBox="0 0 0 0"', f'viewBox="{viewbox_str}"')
    
    # Print dimensions for verification
    print(f"SVG Pattern Dimensions:")
    print(f"X range: {min_x:.2f} to {max_x:.2f}, width: {pattern_width:.2f}")
    print(f"Y range: {min_y:.2f} to {max_y:.2f}, height: {pattern_height:.2f}")
    print(f"ViewBox: {viewbox_str}")
    
    return svg_content

