"""
Industrial analysis callbacks.
"""
from dash import Input, Output, State
import pandas as pd
from data.data_manager import DataManager
from visualizations.industrial_plots import (
    make_industry_bar_figure,
    make_stacked_illegal_legal,
    make_transaction_over_time
)


def register_industrial_callbacks(app):
    """Register all industrial analysis callbacks"""
    
    @app.callback(
        Output('normalize-button', 'children'),
        Output('normalize-button', 'color'),
        Input('normalize-button', 'n_clicks')
    )
    def toggle_normalize_button(n_clicks):
        """Toggle the normalize button state"""
        if not n_clicks:
            n_clicks = 0
        label = "🔄 Denormalize" if (n_clicks % 2 == 1) else "🔄 Normalize"
        color = "success" if (n_clicks % 2 == 1) else "primary"
        return label, color

    @app.callback(
        Output('industry-bar-chart', 'figure'),
        Input('country-dropdown', 'value'),
        Input('normalize-button', 'n_clicks'),
        Input('date-range-picker-industrial', 'start_date'),
        Input('date-range-picker-industrial', 'end_date')
    )
    def build_industry_fig(selected_country, normalize_clicks, start_date, end_date):
        """Build industry bar chart with optional filtering and normalization"""
        data_manager = app.data_manager
        data = data_manager.get_data()
        
        # Filter by date range
        if start_date and end_date:
            filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, [selected_country])
        else:
            filtered_data = data[data['Country'] == selected_country]
        
        return make_stacked_illegal_legal(selected_country, normalize_clicks or 0, filtered_data)

    @app.callback(
        Output('transactions-over-time', 'figure'),
        Input('industry-dropdown', 'value'),
        Input('country-dropdown-multi', 'value'),
        Input('date-range-picker-industrial', 'start_date'),
        Input('date-range-picker-industrial', 'end_date'),
        Input('window-size-slider', 'value')
    )
    def update_transactions_over_time(selected_industries, selected_countries, start_date, end_date, window_size):
        """Update transactions over time chart"""
        data_manager = app.data_manager
        data = data_manager.get_data()
        iso_a3_dict = data_manager.iso_a3_dict
        
        # Filter data by date range
        if start_date and end_date:
            filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, None)
        else:
            filtered_data = data
        
        return make_transaction_over_time(
            filtered_data, 
            iso_a3_dict, 
            selected_industries, 
            selected_countries, 
            window_size
        )
