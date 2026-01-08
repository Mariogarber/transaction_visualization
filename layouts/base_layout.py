"""
Base layouts and navigation components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_main_layout():
    """Create the main landing page with project explanation and navigation buttons"""
    return html.Div([
        # Header
        html.H1(
            "Money Transactions Analytics Dashboard",
            style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'fontSize': '70px',
                'fontWeight': '700',
                'color': '#2c3e50'
            }
        ),

        # Project Description
        html.Div([
            html.P([
                "Welcome to our comprehensive analytics dashboard for the ",
                html.A(
                    "Global Black Money Transactions Dataset",
                    href="https://www.kaggle.com/datasets/waqi786/global-black-money-transactions-dataset",
                    target="_blank",
                    rel="noopener noreferrer",
                    style={'color': '#0d6efd', 'textDecoration': 'underline', 'fontWeight': '600'}
                ),
                "."
            ],
            style={
                'textAlign': 'center',
                'color': '#34495e',
                'fontSize': '32px',
                'lineHeight': '1.6',
                'marginBottom': '30px',
                'fontWeight': '400'
            }
            ),
            
            html.P([
                "This interactive dashboard provides four comprehensive analysis perspectives of global money transactions data ",
                "spanning from 2013-01-01 to 2014-02-21. Explore patterns, trends, and insights through our specialized analytical tools."
            ],
            style={
                'textAlign': 'center',
                'color': '#5a6c7d',
                'fontSize': '24px',
                'lineHeight': '1.8',
                'marginBottom': '40px',
                'maxWidth': '1200px',
                'margin': '0 auto 40px auto',
                'fontWeight': '300'
            }
            ),
        ], 
        style={
            'backgroundColor': '#f8f9fa',
            'padding': '40px 20px',
            'borderRadius': '15px',
            'marginBottom': '50px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
        ),

        # Navigation Cards
        html.H2(
            "Choose Your Analysis Perspective",
            style={
                'textAlign': 'center',
                'marginBottom': '40px',
                'fontSize': '42px',
                'fontWeight': '600',
                'color': '#2c3e50'
            }
        ),

        # Navigation buttons/cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(" Statistical Overview", 
                               style={'fontSize': '28px', 'fontWeight': '700', 'color': '#e74c3c', 'marginBottom': '20px'}),
                        html.P([
                            "Get comprehensive statistics and insights about global money transactions. ",
                            "View transaction counts, amounts by industry, and key performance indicators across different countries and time periods."
                        ], style={'fontSize': '18px', 'color': '#5a6c7d', 'lineHeight': '1.6', 'marginBottom': '25px'}),
                        dbc.Button(
                            "Explore Statistics",
                            id="nav-statistical",
                            color="danger",
                            size="lg",
                            style={'fontSize': '18px', 'fontWeight': '600', 'height': '50px', 'width': '100%'}
                        )
                    ])
                ], style={'height': '300px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'border': 'none'})
            ], width=12, lg=6, style={'marginBottom': '30px'}),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(" Geographical Analysis", 
                               style={'fontSize': '28px', 'fontWeight': '700', 'color': '#3498db', 'marginBottom': '20px'}),
                        html.P([
                            "Explore the geographical distribution of money transactions with interactive maps. ",
                            "Analyze cross-border flows, identify regional patterns, and understand global transaction networks."
                        ], style={'fontSize': '18px', 'color': '#5a6c7d', 'lineHeight': '1.6', 'marginBottom': '25px'}),
                        dbc.Button(
                            "Explore Geography",
                            id="nav-geographical",
                            color="primary",
                            size="lg",
                            style={'fontSize': '18px', 'fontWeight': '600', 'height': '50px', 'width': '100%'}
                        )
                    ])
                ], style={'height': '300px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'border': 'none'})
            ], width=12, lg=6, style={'marginBottom': '30px'}),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(" Industrial Analysis", 
                               style={'fontSize': '28px', 'fontWeight': '700', 'color': '#2ecc71', 'marginBottom': '20px'}),
                        html.P([
                            "Dive deep into industry-specific transaction patterns and trends. ",
                            "Analyze spending patterns across different sectors and identify potential risk areas by industry classification."
                        ], style={'fontSize': '18px', 'color': '#5a6c7d', 'lineHeight': '1.6', 'marginBottom': '25px'}),
                        dbc.Button(
                            "Explore Industries",
                            id="nav-industrial",
                            color="success",
                            size="lg",
                            style={'fontSize': '18px', 'fontWeight': '600', 'height': '50px', 'width': '100%'}
                        )
                    ])
                ], style={'height': '300px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'border': 'none'})
            ], width=12, lg=6, style={'marginBottom': '30px'}),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(" Risk Analysis", 
                               style={'fontSize': '28px', 'fontWeight': '700', 'color': '#f39c12', 'marginBottom': '20px'}),
                        html.P([
                            "Advanced risk assessment and money laundering detection analysis. ",
                            "Explore risk scores, shell company networks, and tax haven routing patterns with sophisticated visualizations."
                        ], style={'fontSize': '18px', 'color': '#5a6c7d', 'lineHeight': '1.6', 'marginBottom': '25px'}),
                        dbc.Button(
                            "Analyze Risks",
                            id="nav-risk-analysis",
                            color="warning",
                            size="lg",
                            style={'fontSize': '18px', 'fontWeight': '600', 'height': '50px', 'width': '100%'}
                        )
                    ])
                ], style={'height': '300px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'border': 'none'})
            ], width=12, lg=6, style={'marginBottom': '30px'})
        ], justify="center"),

        # Footer
        html.Div([
            html.Hr(style={'marginTop': '60px', 'marginBottom': '30px', 'border': '2px solid #bdc3c7'}),
            html.P([
                "💡 Tip: Each section provides interactive controls to filter data by date range, countries, and other parameters. ",
                "Use the navigation bar at the top to switch between different analysis perspectives."
            ],
            style={
                'textAlign': 'center',
                'color': '#7f8c8d',
                'fontSize': '18px',
                'fontStyle': 'italic',
                'lineHeight': '1.6'
            })
        ])
        
    ], style={'padding': '40px 60px', 'backgroundColor': '#ffffff'})


def create_navigation_bar(active_section=None):
    """Create the navigation bar for all pages"""
    nav_items = [
        {"id": "nav-statistical", "label": "📊 Statistical", "color": "danger"},
        {"id": "nav-geographical", "label": "🗺️ Geographical", "color": "primary"}, 
        {"id": "nav-industrial", "label": "🏢 Industrial", "color": "success"},
        {"id": "nav-risk-analysis", "label": "⚠️ Risk Analysis", "color": "warning"}
    ]
    
    buttons = []
    for item in nav_items:
        is_active = active_section == item["id"].replace("nav-", "")
        
        button = dbc.Button(
            item["label"],
            id=item["id"],
            color=item["color"],
            size="lg",
            outline=not is_active,
            style={
                'fontSize': '18px', 
                'fontWeight': '700' if is_active else '600',
                'marginRight': '15px',
                'marginBottom': '10px',
                'borderWidth': '2px'
            }
        )
        buttons.append(button)
    
    return html.Div([
        html.Div(buttons, 
                style={'textAlign': 'center', 'marginBottom': '30px'}),
        html.Hr(style={'border': '2px solid #ecf0f1', 'marginBottom': '30px'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '25px 30px 15px 30px', 'borderRadius': '10px'})