"""
Risk analysis callbacks.
"""
from dash import Input, Output, State, no_update, callback_context, html
from data.data_manager import DataManager
from visualizations.risk_plots import (
    make_risk_distribution_analysis,
    make_transaction_amount_analysis,
    make_shell_companies_analysis,
    make_tax_haven_flow_analysis
)


def register_risk_callbacks(app):

    import dash_cytoscape as cyto
    from visualizations.shell_network import make_shell_network_elements

    @app.callback(
        Output('shell-network-graph-container', 'children'),
        Input('network-risk-slider', 'value'),
        Input('industry-selection-risk', 'value'),
        Input('network-country-dropdown', 'value'),
        Input('network-industry-dropdown', 'value'),
        Input('network-amount-slider', 'value'),
        Input('network-top-n-input', 'value'),
    )
    def update_shell_network_graph(risk_range, selected_industries, filter_countries, filter_industries, amount_range, top_n):
        data_manager = app.data_manager
        dataset = data_manager.get_data()
        # Filter by main industry selection
        if selected_industries:
            dataset = dataset[dataset['Industry'].isin(selected_industries)]
        # Optional country filter
        if filter_countries:
            dataset = dataset[dataset['Country'].isin(filter_countries)]
        # Optional industry filter
        if filter_industries:
            dataset = dataset[dataset['Industry'].isin(filter_industries)]
        # Filter by amount range
        if amount_range:
            dataset = dataset[(dataset['Amount (USD)'] >= amount_range[0]) & (dataset['Amount (USD)'] <= amount_range[1])]
        # Limit to user-selected number of transactions (max 250)
        if not top_n or top_n > 250:
            top_n = 250
        dataset = dataset.head(top_n)
        elements, stylesheet = make_shell_network_elements(dataset, risk_range)
        if not elements:
            return html.Div("No network data for selected filters.", style={'textAlign': 'center', 'color': '#888', 'fontSize': '18px', 'margin': '30px'})
        
        # Create legend
        legend = html.Div([
            html.Div("Legend", style={
                'fontSize': '18px',
                'fontWeight': 'bold',
                'marginBottom': '10px',
                'color': '#34495e'
            }),
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': '15px',
                        'height': '15px',
                        'borderRadius': '50%',
                        'backgroundColor': '#2980b9',
                        'display': 'inline-block',
                        'marginRight': '10px'
                    }),
                    html.Span("Person Involved", style={'fontSize': '14px', 'color': '#5a6c7d'})
                ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'}),
                html.Div([
                    html.Div(style={
                        'width': '15px',
                        'height': '15px',
                        'borderRadius': '50%',
                        'backgroundColor': '#e67e22',
                        'display': 'inline-block',
                        'marginRight': '10px'
                    }),
                    html.Span("Shell Company", style={'fontSize': '14px', 'color': '#5a6c7d'})
                ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'}),
                html.Div([
                    html.Div(style={
                        'width': '15px',
                        'height': '15px',
                        'borderRadius': '50%',
                        'backgroundColor': '#27ae60',
                        'display': 'inline-block',
                        'marginRight': '10px'
                    }),
                    html.Span("Country", style={'fontSize': '14px', 'color': '#5a6c7d'})
                ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'}),
                html.Div([
                    html.Div("→", style={
                        'fontSize': '18px',
                        'display': 'inline-block',
                        'marginRight': '10px',
                        'color': '#34495e',
                        'fontWeight': 'bold'
                    }),
                    html.Span("Transaction Flow", style={'fontSize': '14px', 'color': '#5a6c7d'})
                ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'}),
            ])
        ], style={
            'position': 'absolute',
            'top': '10px',
            'right': '10px',
            'backgroundColor': 'rgba(255, 255, 255, 0.95)',
            'padding': '15px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.15)',
            'zIndex': '1000',
            'border': '1px solid #e0e6ed'
        })
        
        return html.Div([
            legend,
            cyto.Cytoscape(
                id='shell-network-graph',
                elements=elements,
                layout={'name': 'cose'},
                stylesheet=stylesheet,
                style={'width': '100%', 'height': '600px', 'background': '#f8f9fa', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'},
                minZoom=0.3,
                maxZoom=3,
                zoom=1,
                pan={'x': 0, 'y': 0}
            )
        ], style={'position': 'relative'})
    
    @app.callback(
        Output('risk-distribution-plot', 'figure'),
        Input('url', 'pathname')  # Trigger when entering risk page
    )
    def update_risk_distribution_plot(pathname):
        """Update risk distribution analysis plot"""
        if pathname != '/risk':
            return no_update
            
        data_manager = app.data_manager
        dataset = data_manager.get_data()
        
        if dataset.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_risk_distribution_analysis(dataset)

    @app.callback(
        Output('amount-risk-plot', 'figure'),
        Input('industry-selection-risk', 'value'),
        Input('toggle-clustering-risk', 'n_clicks')
    )
    def update_amount_risk_plot(selected_industries, clustering_clicks):
        """Update transaction amount vs risk analysis plot"""
        data_manager = app.data_manager
        dataset = data_manager.get_data()
        
        # Filter by selected industries
        if selected_industries:
            dataset = dataset[dataset['Industry'].isin(selected_industries)]

        use_clustering = not clustering_clicks or (clustering_clicks % 2 == 1)
        
        return make_transaction_amount_analysis(dataset, use_clustering)

    @app.callback(
        Output('shell-companies-plot', 'figure'),
        Input('industry-selection-risk', 'value')
    )
    def update_shell_companies_plot(selected_industries):
        """Update shell companies analysis plot"""
        data_manager = app.data_manager
        dataset = data_manager.get_data()
        
        # Filter by selected industries
        if selected_industries:
            dataset = dataset[dataset['Industry'].isin(selected_industries)]
        
        if dataset.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for selected industries",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_shell_companies_analysis(dataset)

    @app.callback(
        Output('tax-haven-flow-plot', 'figure'),
        Input('industry-selection-risk', 'value')
    )
    def update_tax_haven_flow_plot(selected_industries):
        """Update tax haven flow analysis plot"""
        data_manager = app.data_manager
        dataset = data_manager.get_data()
        
        # Filter by selected industries
        if selected_industries:
            dataset = dataset[dataset['Industry'].isin(selected_industries)]
        
        if dataset.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for selected industries",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return fig
            
        return make_tax_haven_flow_analysis(dataset)

    @app.callback(
        Output('industry-selection-risk', 'value'),
        Input('select-all-industries-risk', 'n_clicks'),
        Input('clear-all-industries-risk', 'n_clicks'),
        State('industry-selection-risk', 'options')
    )
    def update_industry_selection(select_all_clicks, clear_all_clicks, options):
        """Update industry selection based on Select All or Clear All buttons"""
        ctx = callback_context
        if not ctx.triggered:
            # Default to all industries selected
            return [option['value'] for option in options]
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'select-all-industries-risk':
            return [option['value'] for option in options]
        elif trigger_id == 'clear-all-industries-risk':
            return []
        
        return no_update

    @app.callback(
        Output('toggle-clustering-risk', 'children'),
        Output('toggle-clustering-risk', 'color'),
        Input('toggle-clustering-risk', 'n_clicks')
    )
    def toggle_clustering_button(n_clicks):
        """Toggle the clustering button state"""
        if not n_clicks:
            n_clicks = 0
        
        if n_clicks % 2 == 1:
            return " Show All Points", "success"
        else:
            return " Reduce Samples", "warning"
