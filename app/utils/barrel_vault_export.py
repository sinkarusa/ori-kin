import os
import tempfile
import base64
from io import BytesIO

import ezdxf

from .barrel_vault import generate_barrel_vault_pattern
from .config_loader import get_barrel_vault_config


def create_barrel_vault_dxf(r, n, m, omega, h, fold_color_1=None, fold_color_2=None, connecting_color=None, fold_width=None, connecting_width=None):
    """Create DXF file for barrel vault pattern"""
    # Load configuration from YAML file
    config = get_barrel_vault_config()
    
    # Use provided values or defaults from config
    fold_color_1 = fold_color_1 or config['colors']['fold_color_1']
    fold_color_2 = fold_color_2 or config['colors']['fold_color_2']
    connecting_color = connecting_color or config['colors']['connecting_color']
    fold_width = fold_width or config['line_widths']['fold_width']
    connecting_width = connecting_width or config['line_widths']['connecting_width']
    connecting_line_style = config['line_styles']['connecting_line_style']
    
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

        # Get pattern using existing generate_barrel_vault_pattern function
        traces = generate_barrel_vault_pattern(r, n, m, omega, h, fold_color_1, fold_color_2, connecting_color, fold_width, connecting_width)
        
        # Track pattern extents for verification
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # Add pattern lines using exact coordinates from generate_pattern
        for trace in traces:
            # For barrel vault pattern, the traces are go.Scatter objects, not dictionaries
            # Extract x, y, and line properties safely
            if hasattr(trace, 'x') and hasattr(trace, 'y') and hasattr(trace, 'line'):
                # This is a go.Scatter object
                x, y = trace.x, trace.y
                line_color = trace.line.color
            else:
                # This is a dictionary (like in the pseudo dome pattern)
                x, y = trace['x'], trace['y']
                line_color = trace['line']['color']
            
            if len(x) == 2 and all(coord is not None for coord in x + y):
                start = (float(x[0]), float(y[0]))
                end = (float(x[1]), float(y[1]))
                
                min_x = min(min_x, start[0], end[0])
                max_x = max(max_x, start[0], end[0])
                min_y = min(min_y, start[1], end[1])
                max_y = max(max_y, start[1], end[1])
                
                # Add lines with appropriate line type and color
                # Apply line style based on configuration
                if line_color == connecting_color:
                    linetype = 'CONTINUOUS'
                    if connecting_line_style in ['dash', 'dot', 'dashdot']:
                        linetype = connecting_line_style.upper()
                    
                    # Use the color mapping function for connecting color
                    dxf_color = get_dxf_color(connecting_color)
                    msp.add_line(start, end, dxfattribs={
                        'linetype': linetype,
                        'color': dxf_color,
                        'lineweight': connecting_width
                    })
                else:
                    # Determine if this is fold_color_1 or fold_color_2
                    dxf_color = get_dxf_color(line_color)
                    msp.add_line(start, end, dxfattribs={
                        'color': dxf_color,
                        'lineweight': fold_width
                    })

        # Print exact dimensions for verification
        print(f"Barrel Vault DXF Pattern Dimensions:")
        print(f"X extent: {min_x:.6f}m to {max_x:.6f}m (width: {(max_x - min_x):.6f}m)")
        print(f"Y extent: {min_y:.6f}m to {max_y:.6f}m (height: {(max_y - min_y):.6f}m)")
        
        # Add verification rectangle at pattern extents
        msp.add_lwpolyline([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y), (min_x, min_y)], dxfattribs={'color': 3})  # Green

        # Setup dimension style
        dimstyle = doc.dimstyles.new('METRIC')
        dimstyle.dxf.dimscale = 1.0
        dimstyle.dxf.dimexe = 0.05
        dimstyle.dxf.dimexo = 0.05
        dimstyle.dxf.dimasz = 0.1
        dimstyle.dxf.dimtxt = 0.2
        
        # Add width dimension
        msp.add_linear_dim(
            base=(0, min_y - 0.5),
            p1=(min_x, 0),
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
        # Convert BytesIO to base64 string for Dash
        encoded = base64.b64encode(buffer.read()).decode()
        return encoded

    except Exception as e:
        print(f"Error creating DXF: {str(e)}")
        print(f"Error details: {str(e.__class__.__name__)}")
        raise
