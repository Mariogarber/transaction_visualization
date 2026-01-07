"""
Application factory for creating the Dash application with modular architecture.
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from data.data_manager import DataManager
from callbacks import register_all_callbacks
from layouts.base_layout import create_main_layout
from layouts.statistical_layout import create_statistical_layout
from layouts.geographical_layout import create_geographical_layout
from layouts.industrial_layout import create_industrial_layout
from layouts.risk_layout import create_risk_layout


def create_app():
    """Create and configure the Dash app."""
    
    # Initialize Dash app
    app = dash.Dash(__name__, 
                    external_stylesheets=[
                        dbc.themes.BOOTSTRAP,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
                    ],
                    suppress_callback_exceptions=True)
    
    # Load data
    data_manager = DataManager()
    data = data_manager.get_data()
    gdf = data_manager.geodata
    iso_a3_dict = data_manager.iso_a3_dict
    
    # Store data in app for callbacks to access
    app.data = data
    app.data_manager = data_manager
    app.gdf = gdf
    app.iso_a3_dict = iso_a3_dict
    
    # App layout with URL routing
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])
    
    # Register all callbacks
    register_all_callbacks(app)
    
    return app