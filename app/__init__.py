from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


def create_app():
    # Initialize the app with Bootstrap for the modal component
    app = Dash(
        __name__,
        suppress_callback_exceptions=True,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://use.fontawesome.com/releases/v5.15.4/css/all.css'  # For the question mark icon
        ]
    )
    
    # Import components after app creation to avoid circular imports
    from .callbacks import register_callbacks
    from .layout import (
        create_barrel_vault_layout,
        create_double_barrel_vault_layout,
        create_landing_layout,
        create_pseudo_dome_layout,
    )

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/pseudo-dome':
            return create_pseudo_dome_layout()
        elif pathname == '/barrel-vault':
            return create_barrel_vault_layout()
        elif pathname == '/double-barrel-vault':
            return create_double_barrel_vault_layout()
        else:
            return create_landing_layout()

    register_callbacks(app)
    
    return app