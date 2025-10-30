from dash import dcc, html
from dash.dcc import Loading

def create_layout(data):
    layout = html.Div([
        html.Iframe(id='reported-map', style={'width': '100%', 'height': '600px'}),
        dcc.DatePickerSingle(
            id='date-picker',
            date=data['Date'].min(),
            display_format='YYYY-MM-DD',
            min_date_allowed=data['Date'].min(),
            max_date_allowed=data['Date'].max()
        ),
        # replace button with checkboxes for transaction type selection
        dcc.Checklist(
            id='transaction-checklist',
            options=[
                {'label': 'Origin Transactions', 'value': 'origin'},
                {'label': 'Destiny Transactions', 'value': 'destiny'}
            ],
            value=['origin', 'destiny'],
            inline=True
        ),
        dcc.Dropdown(id='country-selector',
            options=[{'label': country, 'value': country} for country in data['Country'].unique()] + [{'label': 'ALL', 'value': 'ALL'}],
            value='ALL',
            clearable=False
        ),
        Loading(
            id='loading-arrow-map',
            children=dcc.Graph(id='transaction-arrow-map', style={'width': '100%', 'height': '400px'}),
            type='graph',
            color="#8afa7c",
            fullscreen=False
        ),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
            value='USA',
            clearable=False
        ),
        html.Button('Normalize', id='normalize-button', n_clicks=0, style={'margin': '10px'}),
        Loading(
            id='loading-industry-bar-chart',
            children=dcc.Graph(id='industry-bar-chart'),
            type='graph',
            fullscreen=False,
            color="#ffcc00",
            ),
        #dropdown by industry
        dcc.Dropdown(id='industry-dropdown',
            options=[{'label': industry, 'value': industry} for industry in data['Industry'].unique()],
            value=data['Industry'].unique().tolist(),
            multi=True,
            clearable=False
        ),
        dcc.Dropdown(id='country-dropdown-multi', 
            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
            value=data['Country'].unique().tolist(),
            multi=True,
            clearable=False
        ),
        Loading(
            id='loading-transaction-over-time',
            children=dcc.Graph(id='transactions-over-time', style={'width': '100%', 'height': '600px'}),
            type='graph',
            fullscreen=False,
            color="#ff5733",
            style={'marginBottom': '50px'}
        )
])
    return layout

from dash import dcc, html

def create_layout_v2(data):
    layout = html.Div([
        html.H1("Money Transactions Analytics Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),

        # ===============================
        # SECTION: GEOGRAPHICAL ANALYSIS
        # ===============================
        html.Div([
            html.H2("Geographical Analysis", style={'marginBottom': '20px'}),


            html.Div([
                html.H3("Reported Transactions Map"),
                html.Iframe(id='reported-map', style={'width': '100%', 'height': '500px', 'border': '1px solid #ccc', 'borderRadius': '8px'}),
            ], style={'marginBottom': '40px'}),

            html.Div([
                html.Div([
                    html.Label("📅 Date:", style={'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(
                        id='date-picker',
                        date=data['Date'].min(),
                        display_format='YYYY-MM-DD',
                        min_date_allowed=data['Date'].min(),
                        max_date_allowed=data['Date'].max(),
                        style={'width': '100%'}
                    ),
                ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '20px'}),

                html.Div([
                    html.Label("Transaction Type:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id='transaction-checklist',
                        options=[
                            {'label': 'Origin', 'value': 'origin'},
                            {'label': 'Destination', 'value': 'destiny'}
                        ],
                        value=['origin', 'destiny'],
                        inline=True,
                        inputStyle={'marginRight': '5px'}
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                html.Div([
                    html.Label("País:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='country-selector',
                        options=[{'label': country, 'value': country} for country in data['Country'].unique()] +
                                [{'label': 'ALL', 'value': 'ALL'}],
                        value='ALL',
                        clearable=False,
                        style={'width': '100%'}
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '20px'}),
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.H3("Transaction Flux Map (Origin & Destination)"),
                dcc.Graph(id='transaction-arrow-map', style={'width': '100%', 'height': '400px'})
            ])
        ], style={
            'border': '1px solid #d9d9d9',
            'borderRadius': '10px',
            'padding': '25px',
            'marginBottom': '50px',
            'backgroundColor': '#f9f9f9'
        }),

        # ===============================
        # SECTION: INDUSTRIAL ANALYSIS
        # ===============================
        html.Div([
            html.H2("Industrial Analysis", style={'marginBottom': '20px'}),

            html.Div([
                html.Div([
                    html.Label("Country:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                        value='USA',
                        clearable=False,
                        style={'width': '100%'}
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}),

                html.Div([
                    html.Button('🔄 Normalize', id='normalize-button', n_clicks=0,
                                style={'marginTop': '25px', 'width': '150px', 'height': '40px', 'borderRadius': '8px'})
                ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'marginBottom': '30px'}),

            html.Div([
                html.H3("Transaction Distribution by Industry"),
                dcc.Graph(id='industry-bar-chart', style={'width': '100%', 'height': '400px'})
            ], style={'marginBottom': '40px'}),

            html.Div([
                html.Div([
                    html.Label("Industry Selection:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='industry-dropdown',
                        options=[{'label': industry, 'value': industry} for industry in data['Industry'].unique()],
                        value=data['Industry'].unique().tolist(),
                        multi=True,
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'width': '45%', 'display': 'inline-block', 'paddingRight': '20px'}),

                html.Div([
                    html.Label("Country Selection:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='country-dropdown-multi',
                        options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                        value=data['Country'].unique().tolist(),
                        multi=True,
                        clearable=False,
                        style={'width': '100%'}
                    )
                ], style={'width': '45%', 'display': 'inline-block'}),
            ], style={'marginBottom': '30px'}),

            html.Div([
                html.H3("Evolución de Transacciones en el Tiempo"),
                html.Label("Tamaño de Ventana para Promedio Móvil:", style={'fontWeight': 'bold'}),
                dcc.Slider(
                    id='window-size-slider',
                    min=1,
                    max=25,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(1, 26, 5)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    updatemode='drag'
                ),
                dcc.Graph(id='transactions-over-time', style={'width': '100%', 'height': '600px'})
            ])
        ], style={
            'border': '1px solid #d9d9d9',
            'borderRadius': '10px',
            'padding': '25px',
            'backgroundColor': '#f9f9f9',
            'marginBottom': '50px'
        })
    ], style={'fontFamily': 'Arial, sans-serif', 'padding': '30px'})

    return layout
