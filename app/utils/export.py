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
                # Apply line style based on configuration
                if trace['line']['color'] == radial_color:
                    linetype = 'CONTINUOUS'
                    if radial_line_style == 'dash':
                        linetype = 'DASHED'
                    elif radial_line_style == 'dot':
                        linetype = 'DOTTED'
                    elif radial_line_style == 'dashdot':
                        linetype = 'DASHDOT'
                    
                    msp.add_line(start, end, dxfattribs={
                        'linetype': linetype,
                        'color': 5  # Blue=5
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
            # Apply line style based on configuration
            stroke_dasharray = 'none'
            if dash == 'dash' or (color == radial_color and radial_line_style == 'dash'):
                stroke_dasharray = '5,5'
            elif dash == 'dot' or (color == radial_color and radial_line_style == 'dot'):
                stroke_dasharray = '1,3'
            elif dash == 'dashdot' or (color == radial_color and radial_line_style == 'dashdot'):
                stroke_dasharray = '5,2,1,2'
            line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{stroke_dasharray}" />'
            svg_lines.append(line)
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)
