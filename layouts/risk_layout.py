"""
Risk analysis layout components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_navigation_bar


def create_risk_layout(data):
    """Create the risk analysis page layout"""
    return html.Div([
        create_navigation_bar('risk'),
        
        html.Div([
            html.H1(" Risk Analysis", 
                   style={'marginBottom': '30px', 'fontSize': '50px', 'fontWeight': '700', 'textAlign': 'center', 'color': '#9b59b6'}),
            
            html.P([
                "Advanced risk assessment and money laundering detection analysis. ",
                "This section provides sophisticated visualizations to identify patterns in risk scores, ",
                "transaction amounts, shell company usage, and money flows through tax havens."
            ],
            style={
                'textAlign': 'center',
                'color': '#5a6c7d',
                'fontSize': '20px',
                'lineHeight': '1.8',
                'marginBottom': '40px',
                'maxWidth': '1000px',
                'margin': '0 auto 40px auto'
            }),
            
            # Risk Distribution Analysis
            html.Div([
                html.H2(" Risk Score Distribution Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Comprehensive analysis of money laundering risk score distributions across legal and illegal transactions.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='risk-distribution-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
            # Transaction Amount Analysis
            html.Div([
                html.H2(" Transaction Amount vs Risk Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Interactive scatter plot showing correlations between transaction amounts, risk scores, and other factors.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                
                # Industry Selection Panel
                html.Div([
                    html.Label(" Select Industries to Analyze:", 
                              style={'fontSize': '18px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '10px'}),
                    dcc.Checklist(
                        id='industry-selection-risk',
                        options=[
                            {'label': f' {industry}', 'value': industry} 
                            for industry in sorted(data['Industry'].unique())
                        ],
                        value=sorted(data['Industry'].unique()),  # All selected by default
                        inline=True,
                        style={'marginBottom': '20px'},
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'marginRight': '20px', 'fontSize': '14px', 'color': '#5a6c7d'}
                    ),
                    html.Div([
                        dbc.Button(
                            "Select All", 
                            id="select-all-industries-risk", 
                            color="primary", 
                            size="sm",
                            style={'marginRight': '10px'}
                        ),
                        dbc.Button(
                            "Clear All", 
                            id="clear-all-industries-risk", 
                            color="secondary", 
                            size="sm",
                            style={'marginRight': '10px'}
                        ),
                        dbc.Button(
                            " Reduce Samples", 
                            id="toggle-clustering-risk", 
                            color="warning", 
                            size="sm",
                            style={'marginLeft': '20px'}
                        )
                    ], style={'marginBottom': '20px'})
                ], style={
                    'backgroundColor': '#ffffff', 
                    'padding': '20px', 
                    'borderRadius': '8px',
                    'border': '1px solid #e0e6ed',
                    'marginBottom': '20px'
                }),
                
                dcc.Graph(id='amount-risk-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
            # Shell Companies Analysis
            html.Div([
                html.H2(" Shell Companies Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Detailed analysis of shell company usage patterns across different industries and transaction types.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='shell-companies-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
            # Tax Haven Flow Analysis
            html.Div([
                html.H2(" Tax Haven Flow Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Sankey diagram showing money flows from source countries through destinations to tax havens.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='tax-haven-flow-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
        ], style={'padding': '20px'})
    ])