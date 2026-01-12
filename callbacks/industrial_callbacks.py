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
    from dash.dependencies import State
    @app.callback(
        Output('sarima-predictor-graph', 'figure'),
        Output('sarima-nclicks-store', 'data'),
        Input('sarima-country-dropdown', 'value'),
        Input('sarima-industry-dropdown', 'value'),
        Input('sarima-date-range-picker', 'start_date'),
        Input('sarima-date-range-picker', 'end_date'),
        Input('sarima-prediction-periods', 'value'),
        Input('sarima-run-button', 'n_clicks'),
        State('sarima-nclicks-store', 'data')
    )
    def update_sarima_predictor(selected_country, selected_industries, train_start, train_end, forecast_periods, n_clicks, last_n_clicks):
        data_manager = app.data_manager
        data = data_manager.get_data()
        if not selected_country or not selected_industries or not train_start or not train_end or not forecast_periods:
            return {"layout": {"title": "Select all parameters for SARIMA prediction."}}, n_clicks
        if isinstance(selected_industries, str):
            selected_industries = [selected_industries]
        import plotly.graph_objects as go
        import pandas as pd
        # Always show the train time series
        df = data.copy()
        df = df[(df['Country'] == selected_country) & (df['Industry'].isin(selected_industries))]
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        mask = (df['Date'] >= pd.to_datetime(train_start)) & (df['Date'] <= pd.to_datetime(train_end))
        train_df = df.loc[mask]
        ts = train_df.groupby('Date')['Amount (USD)'].sum().asfreq('D').fillna(0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts.index, y=ts.values, mode='lines+markers', name='Train Data'))
        fig.update_layout(
            title=f'SARIMA Spend Prediction ({selected_country}, {", ".join(selected_industries)})',
            xaxis_title='Date',
            yaxis_title='Amount (USD)',
            template='plotly_white',
            height=500
        )
        # Only run SARIMA if button pressed and n_clicks increased
        if n_clicks and last_n_clicks is not None and n_clicks > last_n_clicks:
            from visualizations.industrial_plots import make_sarima_predictor_figure
            return make_sarima_predictor_figure(data, selected_country, selected_industries, train_start, train_end, forecast_periods), n_clicks
        return fig, n_clicks
    
    @app.callback(
        Output('normalize-button', 'children'),
        Output('normalize-button', 'color'),
        Input('normalize-button', 'n_clicks')
    )
    def toggle_normalize_button(n_clicks):
        """Toggle the normalize button state"""
        if not n_clicks:
            n_clicks = 0
        label = " Denormalize" if (n_clicks % 2 == 1) else " Normalize"
        color = "success" if (n_clicks % 2 == 1) else "primary"
        return label, color

    @app.callback(
        Output('industry-bar-chart', 'figure'),
        Input('country-dropdown', 'value'),
        Input('normalize-button', 'n_clicks'),
    )
    def build_industry_fig(selected_country, normalize_clicks):
        """Build industry bar chart with optional filtering and normalization"""
        data_manager = app.data_manager
        data = data_manager.get_data()
        
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
