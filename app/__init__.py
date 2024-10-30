from dash import Dash


def create_app():
    app = Dash(__name__)
    
    # Import components after app creation to avoid circular imports
    from .callbacks import register_callbacks
    from .layout import create_layout

    # Set up app layout and callbacks
    app.layout = create_layout()
    register_callbacks(app)
    
    return app