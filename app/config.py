import plotly.express as px

# Color configurations
SET1_COLORS = px.colors.qualitative.Set1
ADDITIONAL_COLORS = ['red', 'black', 'blue', 'green']
ALL_COLORS = SET1_COLORS + ADDITIONAL_COLORS

# Color options for dropdowns
COLOR_OPTIONS = [{'label': f'Color {i+1}', 'value': color} for i, color in enumerate(SET1_COLORS)] + \
                [{'label': color.capitalize(), 'value': color} for color in ADDITIONAL_COLORS]
