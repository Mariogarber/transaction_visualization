"""
Geographical analysis layout components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_navigation_bar


def create_geographical_layout(data):
    """Create the geographical analysis page layout"""
    return html.Div([
        create_navigation_bar('geographical'),
        
        html.Div([
            html.H1(" Geographical Analysis", 
                   style={'marginBottom': '30px', 'fontSize': '50px', 'fontWeight': '700', 'textAlign': 'center', 'color': '#3498db'}),
            
            html.P([
                "Explore the geographical distribution and flow of money transactions across different countries. ",
                "Use the interactive maps and controls to analyze cross-border financial movements."
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

            # Reported Transactions Map
            html.Div([
                html.H3(" Reported Transactions Map", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Overview of reported transactions by country with detailed statistics.",
                    style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '18px', 'lineHeight': '1.6',
                            'marginBottom': '20px'}),
                html.Iframe(id='reported-map', style={'width': '100%', 'height': '500px', 'border': '1px solid #ccc', 'borderRadius': '8px'}),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),

            # Transaction Flux Map
            html.Div([
                html.H3("↔ Transaction Flux Map", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Select a country to view its transactions with other countries over a time period. You can also filter by transaction type. Each arrow represents the aggregate transactions for the selected period.",
                    style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '18px', 'lineHeight': '1.6',
                            'marginBottom': '20px'}),

                # Controls
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Label("📅 Date Range:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                            dcc.DatePickerRange(
                                id='date-range-picker-flux',
                                start_date=data['Date'].min(),
                                end_date=data['Date'].max(),
                                display_format='YYYY-MM-DD',
                                min_date_allowed=data['Date'].min(),
                                max_date_allowed=data['Date'].max(),
                                style={'width': '100%'}
                            )
                        ], width=4),

                        dbc.Col([
                            html.Label("Transaction Type:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                            dcc.Checklist(
                                id='transaction-checklist',
                                options=[
                                    {'label': 'Origin', 'value': 'origin'},
                                    {'label': 'Destination', 'value': 'destiny'}
                                ],
                                value=['destiny'],
                                inline=True,
                                style={'marginTop': '8px'}
                            )
                        ], width=4),

                        dbc.Col([
                            html.Label("Country Selection:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                            dcc.Dropdown(
                                id='country-selector',
                                options=[{'label': country, 'value': country} for country in data['Country'].unique()] + [{'label': 'ALL', 'value': 'ALL'}],
                                value='USA',
                                clearable=False
                            )
                        ], width=4)
                    ], style={'marginBottom': '20px'})
                ]),

                # Map
                dcc.Loading(
                    id='loading-arrow-map',
                    children=html.Div(
                        dcc.Graph(id='transaction-arrow-map', style={'width': '100%', 'height': '640px'}, config={'responsive': True}),
                        style={'paddingBottom': '20px'}
                    ),
                    type='graph',
                    color="#3498db"
                )
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Risk Score Choropleth Map
            html.Div([
                html.H3(" Risk Score by Country", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Interactive world map showing average money laundering risk scores by country. Darker colors indicate higher risk levels.",
                    style={'textAlign': 'left', 'color': '#5a6c7d', 'fontSize': '18px', 'lineHeight': '1.6',
                            'marginBottom': '20px'}),
                
                # Date Range Control for Risk Map
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Label("📅 Date Range:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                            dcc.DatePickerRange(
                                id='date-range-picker-risk-map',
                                start_date=data['Date'].min(),
                                end_date=data['Date'].max(),
                                display_format='YYYY-MM-DD',
                                min_date_allowed=data['Date'].min(),
                                max_date_allowed=data['Date'].max(),
                                style={'width': '100%'}
                            )
                        ], width=4)
                    ], style={'marginBottom': '20px'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),
                
                dcc.Graph(id='risk-choropleth-map')
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '30px'})
            
        ], style={'padding': '0 30px 60px 30px'})
    ])