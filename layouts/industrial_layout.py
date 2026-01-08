"""
Industrial analysis layout components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_navigation_bar


def create_industrial_layout(data):
    """Create the industrial analysis page layout"""
    return html.Div([
        create_navigation_bar('industrial'),
        html.Div([
            html.H1(" Industrial Analysis", 
                   style={'marginBottom': '30px', 'fontSize': '50px', 'fontWeight': '700', 'textAlign': 'center', 'color': '#f39c12'}),
            html.P([
                "Analyze transaction patterns across different industry sectors. ",
                "Discover trends, compare industrial activity, and track changes over time."
            ],
            style={
                'textAlign': 'center',
                'color': '#5a6c7d',
                'fontSize': '20px',
                'lineHeight': '1.6',
                'maxWidth': '800px',
                'margin': '0 auto 40px auto'
            }),
            # Source of Transactions Section
            html.Div([
                html.H3(" Source of Transactions", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),

                # Controls
                dbc.Row([
                    dbc.Col([
                        html.Label("Country Selection:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='country-dropdown',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                            value='USA',
                            clearable=False
                        )
                    ], width=8),
                    dbc.Col([
                        html.Label("Normalization:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dbc.Button(
                            '🔄 Normalize',
                            id='normalize-button',
                            n_clicks=0,
                            color="primary",
                            style={'width': '100%', 'marginTop': '5px'}
                        )
                    ], width=4)
                ], style={'marginBottom': '20px'}),

                # Industry Bar Chart
                dcc.Loading(
                    id='loading-industry-bar-chart',
                    children=dcc.Graph(
                        id='industry-bar-chart',
                        style={'width': '100%', 'height': '500px'},
                        config={'responsive': True}
                    ),
                    type='graph'
                )
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '40px', 'minHeight': '700px'}),

            # --- Time Series Section ---
            html.Div([
                html.H3(" Transactions Over Time", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Track transaction trends across different industries and countries over time.",
                    style={'color': '#5a6c7d', 'fontSize': '18px', 'marginBottom': '20px'}),

                # Controls
                dbc.Row([
                    dbc.Col([
                        html.Label("Industry Selection:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='industry-dropdown',
                            options=[{'label': industry, 'value': industry} for industry in data['Industry'].unique()],
                            value=data['Industry'].unique().tolist(),
                            multi=True,
                            clearable=False
                        )
                    ], width=4),

                    dbc.Col([
                        html.Label("Countries Selection:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='country-dropdown-multi',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                            value=['USA'],
                            multi=True,
                            clearable=False
                        )
                    ], width=4),

                    dbc.Col([
                        html.Label("📅 Date Range:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.DatePickerRange(
                            id='date-range-picker-industrial',
                            start_date=data['Date'].min(),
                            end_date=data['Date'].max(),
                            display_format='YYYY-MM-DD',
                            min_date_allowed=data['Date'].min(),
                            max_date_allowed=data['Date'].max(),
                            style={'width': '100%'}
                        )
                    ], width=4)
                ], style={'marginBottom': '20px'}),

                html.Label("Window Size for Moving Average:", style={'fontWeight': '700', 'marginBottom': '15px', 'fontSize': '18px'}),
                dcc.Slider(
                    id='window-size-slider',
                    min=1, max=25, step=1, value=5,
                    marks={i: str(i) for i in range(1, 26, 5)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    updatemode='drag'
                ),

                # Transaction Over Time Graph
                dcc.Loading(
                    id='loading-transaction-over-time',
                    children=dcc.Graph(
                        id='transactions-over-time',
                        style={'width': '100%', 'height': '800px', 'marginTop': '20px'},
                        config={'responsive': True}
                    ),
                    type='graph',
                    color="#ff5733"
                )
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '40px', 'minHeight': '800px'}),
            
            # --- SARIMA Predictor Section ---
            html.Div([
                html.H3(" SARIMA Spend Predictor", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Forecast future spend using SARIMA model. Select country, industries, and training period.",
                    style={'color': '#5a6c7d', 'fontSize': '18px', 'marginBottom': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.Label("Country:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='sarima-country-dropdown',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                            value='USA',
                            clearable=False
                        )
                    ], width=2),
                    dbc.Col([
                        html.Label("Industries:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Dropdown(
                            id='sarima-industry-dropdown',
                            options=[{'label': industry, 'value': industry} for industry in data['Industry'].unique()],
                            value=data['Industry'].unique().tolist(),
                            multi=True,
                            clearable=False
                        )
                    ], width=3),
                    dbc.Col([
                        html.Label("Train Date Range:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.DatePickerRange(
                            id='sarima-date-range-picker',
                            start_date=data['Date'].min(),
                            end_date=data['Date'].max(),
                            display_format='YYYY-MM-DD',
                            min_date_allowed=data['Date'].min(),
                            max_date_allowed=data['Date'].max(),
                            style={'width': '100%'}
                        )
                    ], width=3),
                    dbc.Col([
                        html.Label("# Predictions:", style={'fontWeight': '700', 'marginBottom': '10px', 'fontSize': '18px'}),
                        dcc.Input(
                            id='sarima-prediction-periods',
                            type='number',
                            min=1,
                            max=60,
                            step=1,
                            value=12,
                            style={'width': '100%', 'marginTop': '5px'}
                        )
                    ], width=2),
                    dbc.Col([
                        html.Label(" ", style={'marginBottom': '10px', 'fontSize': '18px'}),
                        dbc.Button(
                            'Run SARIMA',
                            id='sarima-run-button',
                            n_clicks=0,
                            color='primary',
                            style={'width': '100%', 'marginTop': '32px'}
                        )
                    ], width=2)
                ], style={'marginBottom': '20px'}),
                dcc.Store(id='sarima-nclicks-store', data=0),
                dcc.Loading(
                    id='loading-sarima-predictor',
                    children=dcc.Graph(
                        id='sarima-predictor-graph',
                        style={'width': '100%', 'height': '700px', 'marginTop': '20px'},
                        config={'responsive': True}
                    ),
                    type='graph',
                    color="#2eaf4d"
                )
            ], style={'backgroundColor': '#f8f9fa', 'padding': '25px', 'borderRadius': '10px', 'marginBottom': '40px', 'minHeight': '700px'})
        ], style={'padding': '0 30px 60px 30px'})
    ])