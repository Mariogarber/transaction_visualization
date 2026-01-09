"""
Statistical analysis layout components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_navigation_bar


def create_statistical_layout(data):
    """Create the statistical overview page layout"""
    return html.Div([
        create_navigation_bar('statistical'),
        
        html.Div([
            html.H1(" Statistical Overview", 
                   style={'marginBottom': '30px', 'fontSize': '50px', 'fontWeight': '700', 'textAlign': 'center', 'color': '#e74c3c'}),
            
            html.P([
                "This section provides comprehensive statistics about global money transactions. ",
                "Use the controls below to filter data by date range and countries to get specific insights."
            ],
            style={
                'textAlign': 'center',
                'color': '#5a6c7d',
                'fontSize': '20px',
                'lineHeight': '1.6',
                'maxWidth': '800px',
                'margin': '0 auto 40px auto'
            }
            ),

            # Date Range and Country Selection
            html.Div([
                html.H3(" Filter Controls", style={'marginBottom': '20px', 'fontSize': '28px', 'fontWeight': '700'}),
                
                dbc.Row([
                    dbc.Col([
                        html.Label("📅 Date Range:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.DatePickerRange(
                            id='date-range-picker',
                            start_date=data['Date'].min(),
                            end_date=data['Date'].max(),
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'}
                        )
                    ], width=6),
                    
                    dbc.Col([
                        html.Label("Countries:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='country-dropdown-overview',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                            value=data['Country'].unique().tolist(),
                            multi=True,
                            placeholder="Select countries..."
                        )
                    ], width=6)
                ], className="mb-4")
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),

            # Overview Cards
            html.Div([
                html.H3(" Key Metrics", style={'marginBottom': '20px', 'fontSize': '28px', 'fontWeight': '700'}),
                html.P("These cards show the total number of transactions and the total amount moved in USD for the selected filters.", style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '15px', 'marginBottom': '15px'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Total Transactions", style={'color': '#3498db', 'marginBottom': '10px'}),
                                html.H2(id='total-transactions', style={'color': '#2c3e50', 'fontWeight': '700'})
                            ])
                        ], color="primary", outline=True)
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Total Amount", style={'color': '#e74c3c', 'marginBottom': '10px'}),
                                html.H2(id='total-millions', style={'color': '#2c3e50', 'fontWeight': '700'})
                            ])
                        ], color="danger", outline=True)
                    ], width=6)
                ], style={'marginBottom': '30px'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),

            # Industry Cards
            html.Div([
                html.H3(" Industry Distribution", style={'marginBottom': '20px', 'fontSize': '28px', 'fontWeight': '700'}),
                html.P("Shows the distribution of transactions across different industry sectors.", style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '15px', 'marginBottom': '15px'}),
                html.Div(id='industry-cards')
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Time Trends Analysis
            html.Div([
                html.H3(" Transaction Trends Over Time", style={'marginBottom': '20px', 'fontSize': '28px', 'fontWeight': '700'}),
                html.P("Visualizes how transaction volume and risk scores change over time, helping to spot trends and anomalies.",
                      style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '16px', 'marginBottom': '20px'}),
                dcc.Graph(id='trends-analysis')
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Statistical Analysis Row
            dbc.Row([
                # Correlation Analysis
                dbc.Col([
                    html.Div([
                        html.H3(" Variable Correlations", style={'marginBottom': '20px', 'fontSize': '24px', 'fontWeight': '700'}),
                        html.P("Displays the correlation matrix to show how variables like amount, risk score, and others relate to each other.",
                              style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '14px', 'marginBottom': '15px'}),
                        dcc.Graph(id='correlation-analysis')
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6),
                
                # Summary Statistics
                dbc.Col([
                    html.Div([
                        html.H3(" Summary Statistics", style={'marginBottom': '20px', 'fontSize': '24px', 'fontWeight': '700'}),
                        html.P("Shows key summary statistics (mean, median, etc.) for the main numerical columns in the dataset.",
                              style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '14px', 'marginBottom': '15px'}),
                        dcc.Graph(id='summary-statistics')
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'})
                ], width=6)
            ], style={'marginBottom': '30px'}),
            
            # Amount Distribution Analysis
            html.Div([
                html.H3(" Transaction Amount Analysis", style={'marginBottom': '20px', 'fontSize': '28px', 'fontWeight': '700'}),
                html.P("Shows the distribution of transaction amounts, helping to identify typical values and outliers.",
                      style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '16px', 'marginBottom': '20px'}),
                dcc.Graph(id='amount-distribution-analysis')
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'})
            
        ], style={'padding': '0 30px 60px 30px'})
    ])