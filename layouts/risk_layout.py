"""
Risk analysis layout components.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_navigation_bar


def create_risk_layout(data):

    # Shell Companies Network Graph section
    shell_network_section = html.Div([
        html.H2("Shell Companies Network Graph", style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
        html.P("Interactive network graph showing relationships between people, shell companies, and countries. Edge labels represent risk scores. Use the filters to explore the network. The 'Top N Transactions by Amount' filter limits the graph to the largest transactions.",
                style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
        dbc.Row([
            dbc.Col([
                html.Label("Filter by Country:", style={'fontWeight': '600', 'fontSize': '16px', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='network-country-dropdown',
                    options=[{'label': c, 'value': c} for c in sorted(data['Country'].unique())],
                    multi=True,
                    placeholder="Select countries (optional)",
                    style={'marginBottom': '15px'}
                )
            ], width=4),
            dbc.Col([
                html.Label("Filter by Industry:", style={'fontWeight': '600', 'fontSize': '16px', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='network-industry-dropdown',
                    options=[{'label': i, 'value': i} for i in sorted(data['Industry'].unique())],
                    multi=True,
                    placeholder="Select industries (optional)",
                    style={'marginBottom': '15px'}
                )
            ], width=4),
            dbc.Col([
                html.Label("Transaction Amount Range:", style={'fontWeight': '600', 'fontSize': '16px', 'marginBottom': '5px'}),
                dcc.RangeSlider(
                    id='network-amount-slider',
                    min=float(data['Amount (USD)'].min()),
                    max=float(data['Amount (USD)'].max()),
                    step=1000,
                    value=[float(data['Amount (USD)'].quantile(0.05)), float(data['Amount (USD)'].quantile(0.95))],
                    marks={
                        int(data['Amount (USD)'].min()): f"${int(data['Amount (USD)'].min()):,}",
                        int(data['Amount (USD)'].max()): f"${int(data['Amount (USD)'].max()):,}"
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                    allowCross=False,
                    pushable=1000,
                    updatemode='mouseup',
                ),
                html.Div("Note: Only the first 250 transactions in the selected range will be shown for performance.", style={'fontSize': '12px', 'color': '#888', 'marginTop': '5px'})
            ], width=4),
            dbc.Col([
                html.Label("Number of Transactions to Show (max 250):", style={'fontWeight': '600', 'fontSize': '16px', 'marginBottom': '5px'}),
                dcc.Input(
                    id='network-top-n-input',
                    type='number',
                    min=1,
                    max=250,
                    step=1,
                    value=25,
                    style={'width': '100%', 'marginBottom': '15px'}
                ),
            ], width=4)
        ], style={'marginBottom': '10px'}),
        html.Label("Filter edges by risk score:", style={'fontWeight': '600', 'fontSize': '16px', 'marginBottom': '10px'}),
        html.Div([
            dcc.RangeSlider(
                id='network-risk-slider',
                min=0, max=10, step=1, value=[0, 10],
                marks={i: str(i) for i in range(0, 11)},
                tooltip={"placement": "bottom", "always_visible": True},
                allowCross=False,
                pushable=1,
                updatemode='mouseup',
            )
        ], style={'marginBottom': '30px'}),
        dcc.Loading(
            id='loading-shell-network',
            children=[
                html.Div([
                    html.Div(id='shell-network-graph-container')
                ])
            ],
            type='circle',
            color="#9b59b6"
        )
    ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'})

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
                html.P("Shows the distribution of money laundering risk scores for all transactions. Use this to identify the prevalence of high-risk activity.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='risk-distribution-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
                # Transaction Amount Analysis
                html.Div([
                    html.H2(" Transaction Amount vs Risk Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                    html.P("Scatter plot showing how transaction amounts relate to risk scores and other factors. Use industry selection to focus the analysis.",
                        style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                    html.P("Use this Scatter plot to identigy trends and outliers in transaction amounts relative to their associated risk scores. By selecting specific industries, you can focus on sectors that may exhibit higher risk patterns, helping to pinpoint areas that require further investigation.",
                        style={'fontSize': '14px', 'color': '#95a5a6', 'marginBottom': '20px'}),    
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
                        value=[sorted(data['Industry'].unique())[0]],  # Default to first industry
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
                            "Reduce Samples", 
                            id="toggle-clustering-risk", 
                            color="success", 
                            size="sm",
                            style={'marginLeft': '20px'},
                            n_clicks=1
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
            shell_network_section,
            html.Div([
                html.H2(" Shell Companies Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Shows how shell companies are used in transactions, broken down by industry and transaction type. Useful for spotting suspicious patterns.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='shell-companies-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
            # Tax Haven Flow Analysis
            html.Div([
                html.H2(" Tax Haven Flow Analysis", 
                        style={'fontSize': '32px', 'fontWeight': '600', 'color': '#34495e', 'marginBottom': '20px'}),
                html.P("Sankey diagram visualizing the flow of money from source countries, through destinations, and into tax havens. Helps identify major routes and suspicious flows.",
                      style={'fontSize': '16px', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                dcc.Graph(id='tax-haven-flow-plot')
            ], style={'marginBottom': '50px', 'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px'}),
            
        ], style={'padding': '20px'})
    ])