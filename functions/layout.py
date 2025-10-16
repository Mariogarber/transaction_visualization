from dash import dcc, html

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
        dcc.Graph(id='transaction-arrow-map', style={'width': '100%', 'height': '400px'}),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
            value='USA',
            clearable=False
        ),
        html.Button('Normalize', id='normalize-button', n_clicks=0, style={'margin': '10px'}),
        dcc.Graph(id='industry-bar-chart'),
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
        dcc.Graph(id='transactions-over-time', style={'width': '100%', 'height': '600px'})
])
    return layout

from dash import dcc, html

def create_layout_v2(data):
    layout = html.Div([
        html.H1("Dashboard de Análisis de Transacciones", style={'textAlign': 'center', 'marginBottom': '30px'}),

        # ===============================
        # SECCIÓN: ANÁLISIS GEOGRÁFICO
        # ===============================
        html.Div([
            html.H2("Análisis Geográfico", style={'marginBottom': '20px'}),


            html.Div([
                html.H3("Mapa de Transacciones Reportadas"),
                html.Iframe(id='reported-map', style={'width': '100%', 'height': '500px', 'border': '1px solid #ccc', 'borderRadius': '8px'}),
            ], style={'marginBottom': '40px'}),

            html.Div([
                html.Div([
                    html.Label("📅 Fecha:", style={'fontWeight': 'bold'}),
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
                    html.Label("Tipo de Transacción:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        id='transaction-checklist',
                        options=[
                            {'label': 'Origen', 'value': 'origin'},
                            {'label': 'Destino', 'value': 'destiny'}
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
                html.H3("Flujos de Transacciones (Origen/Destino)"),
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
        # SECCIÓN: ANÁLISIS INDUSTRIAL
        # ===============================
        html.Div([
            html.H2("Análisis Industrial", style={'marginBottom': '20px'}),

            html.Div([
                html.Div([
                    html.Label("País:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                        value='USA',
                        clearable=False,
                        style={'width': '100%'}
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '20px'}),

                html.Div([
                    html.Button('🔄 Normalizar', id='normalize-button', n_clicks=0,
                                style={'marginTop': '25px', 'width': '150px', 'height': '40px', 'borderRadius': '8px'})
                ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'marginBottom': '30px'}),

            html.Div([
                html.H3("Distribución de Transacciones por Industria"),
                dcc.Graph(id='industry-bar-chart', style={'width': '100%', 'height': '400px'})
            ], style={'marginBottom': '40px'}),

            html.Div([
                html.Div([
                    html.Label("Selección de Industria:", style={'fontWeight': 'bold'}),
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
                    html.Label("Selección de País:", style={'fontWeight': 'bold'}),
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
