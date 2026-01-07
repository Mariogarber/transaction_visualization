"""
Geographical analysis callbacks.
"""
from dash import Input, Output
import pandas as pd
from data.data_manager import DataManager
from visualizations.geographical_plots import (
    make_info_folium_map,
    make_transaction_arrow_map,
    make_risk_score_choropleth_map
)


def register_geographical_callbacks(app):
    """Register all geographical analysis callbacks"""
    
    @app.callback(
        Output('reported-map', 'srcDoc'),
        Input('reported-map', 'id')
    )
    def update_folium_map(_):
        """Update the Folium map with transaction information"""
        data_manager = app.data_manager
        folium_map_info = data_manager.set_folium_data()
        folium_map = make_info_folium_map(**folium_map_info)
        return folium_map

    @app.callback(
        Output('transaction-arrow-map', 'figure'),
        Input('date-range-picker-flux', 'start_date'),
        Input('date-range-picker-flux', 'end_date'),
        Input('transaction-checklist', 'value'),
        Input('country-selector', 'value')
    )
    def update_arrow_map(start_date, end_date, arrow_options, selected_country):
        """Update transaction flow arrow map"""
        data_manager = app.data_manager
        data = data_manager.get_data()
        min_date = data['Date'].min()
        
        if start_date is None:
            start_date = min_date
        if end_date is None:
            end_date = data['Date'].max()
        
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        
        if start_date < min_date:
            start_date = min_date
        
        flows_info = data_manager.filter_flows_range(arrow_options, selected_country, start_date, end_date)
        fig, _ = make_transaction_arrow_map(**flows_info)
        return fig

    @app.callback(
        Output('risk-choropleth-map', 'figure'),
        Input('date-range-picker-risk-map', 'start_date'),
        Input('date-range-picker-risk-map', 'end_date')
    )
    def update_risk_choropleth_map(start_date, end_date):
        """Update risk score choropleth map"""
        data_manager = app.data_manager
        
        # Filter data by date range
        if start_date and end_date:
            filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, None)
        else:
            filtered_data = data_manager.get_data()
        
        if filtered_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected date range",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_risk_score_choropleth_map(filtered_data)
