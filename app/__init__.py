from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    
    # Import components after app creation to avoid circular imports
    from .callbacks import register_callbacks
    from .layout import (
        create_barrel_vault_layout,
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
        else:
            return create_landing_layout()

    register_callbacks(app)
    
    return app