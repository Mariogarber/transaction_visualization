"""
Statistical analysis callbacks.
"""
from dash import Input, Output, no_update
import pandas as pd
from data.data_manager import DataManager
from visualizations.statistical_plots import (
    make_transaction_trends_analysis,
    make_correlation_analysis,
    make_amount_distribution_analysis,
    make_summary_statistics_table
)
from visualizations.industrial_plots import make_industry_bar_figure


def register_statistical_callbacks(app):
    """Register all statistical analysis callbacks"""
    
    @app.callback(
        Output('total-transactions', 'children'),
        Output('total-millions', 'children'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_overview_cards(start_date, end_date, selected_countries):
        """Update overview cards with total transactions and amounts"""
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)
        total_transactions = len(filtered_data)
        total_millions = filtered_data['Amount (USD)'].sum() / 1_000_000
        return f"{total_transactions:,}", f"${total_millions:,.2f}M"

    @app.callback(
        Output('industry-cards', 'children'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_industry_cards(start_date, end_date, selected_countries):
        """Update industry cards with filtered data"""
        from dash import html, dcc
        from visualizations.industrial_plots import make_industry_bar_figure
        
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)

        # Create the industry bar chart
        fig = make_industry_bar_figure(
            filtered_data,
            palette='Plotly'
        )
        
        graph_component = dcc.Graph(
            figure=fig,
            config={'displayModeBar': False, 'responsive': True},
            style={'width': '90%', 'height': '500px', 'margin': '0 auto', 'display': 'block'}
        )

        return html.Div(
            graph_component,
            style={
                'maxWidth': '100%',
                'paddingLeft': 0,
                'paddingRight': 0,
                'width': '100%',
                'textAlign': 'center'
            }
        )

    @app.callback(
        Output('trends-analysis', 'figure'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_trends_analysis(start_date, end_date, selected_countries):
        """Update transaction trends analysis"""
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)
        
        if filtered_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_transaction_trends_analysis(filtered_data)

    @app.callback(
        Output('correlation-analysis', 'figure'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_correlation_analysis(start_date, end_date, selected_countries):
        """Update correlation analysis"""
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)
        
        if filtered_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_correlation_analysis(filtered_data)

    @app.callback(
        Output('amount-distribution-analysis', 'figure'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_amount_distribution_analysis(start_date, end_date, selected_countries):
        """Update amount distribution analysis"""
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)
        
        if filtered_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_amount_distribution_analysis(filtered_data)

    @app.callback(
        Output('summary-statistics', 'figure'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('country-dropdown-overview', 'value')
    )
    def update_summary_statistics(start_date, end_date, selected_countries):
        """Update summary statistics table"""
        data_manager = app.data_manager
        filtered_data = data_manager.filter_data_by_date_and_country(start_date, end_date, selected_countries)
        
        if filtered_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_summary_statistics_table(filtered_data)
