# functions/layout_v2_fixed.py
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_layout_v2(data):
    layout = html.Div([

        # TITULO PRINCIPAL
        html.H1(
            "Money Transactions Analytics Dashboard",
            style={
                'textAlign': 'center',
                'marginBottom': '10px',
                'fontSize': '70px',
                'fontWeight': '700'
            }
        ),

        # STORE para controlar visibilidad de industrias
        dcc.Store(id='visible-industries-store', data=data['Industry'].unique().tolist()),

        # DESCRIPCIÓN
        html.P([
                "With this dashboard, we can do a visual and interactive data analysis of the ",
                html.A(
                    "Global Black Money Transactions Dataset",
                    href="https://www.kaggle.com/datasets/waqi786/global-black-money-transactions-dataset",
                    target="_blank",
                    rel="noopener noreferrer",
                    style={'color': '#0d6efd', 'textDecoration': 'underline', 'fontWeight': '600'}
                ),
                ". Overall, we can get global statistics and specific information about selected countries. "
                "Data ranges from 2013-01-01 to 2014-02-21, so date selections should just be in that range."
            ],
            id='dataset-description',
            style={
                'textAlign': 'center',
                'color': '#000000',
                'fontSize': '30px',
                'lineHeight': '1.6',
                'marginTop': '6px',
                'marginBottom': '20px',
                'padding': '0 12px'
            }
        ),

        # ===========================
        # SECTION: STATISTICAL OVERVIEW
        # ===========================
        html.Div([
            html.H2("📊 Statistical Overview",
                    style={'marginBottom': '10px', 'fontSize': '50px', 'fontWeight': '700'}),

            html.Div([
                html.P(
                    "Select a time range and a set of countries.",
                    id='overview-helper-text-1',
                    style={
                        'textAlign': 'left',
                        'color': '#000000',
                        'fontSize': '1.5rem',
                        'lineHeight': '1.6',
                        'maxWidth': '900px',
                        'marginTop': '6px',
                        'marginBottom': '8px',
                        'padding': '0 12px'
                    }
                ),

                # Controles: DateRange + Countries
                html.Div([
                    html.Div([
                        html.Label("📅 Date:",
                                style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px', 'marginRight': '12px'}),
                        dcc.DatePickerRange(
                            id='date-range-picker',
                            start_date=data['Date'].min(),
                            end_date=data['Date'].max(),
                            display_format='YYYY-MM-DD',
                            min_date_allowed=data['Date'].min(),
                            max_date_allowed=data['Date'].max(),
                            style={'marginRight': '12px', 'minWidth': '260px'}
                        ),
                    ], style={'marginRight': '24px', 'display': 'flex', 'alignItems': 'center'}),

                    html.Div([
                        html.Label("Countries Selection:",
                                style={
                                    'fontWeight': '700',
                                    'marginBottom': '0px',
                                    'fontSize': '25px',
                                    'lineHeight': '1',
                                    'marginRight': '12px',
                                    'whiteSpace': 'nowrap'
                                }
                        ),
                        dcc.Dropdown(
                            id='country-dropdown-overview',
                            options=[{'label': c, 'value': c} for c in data['Country'].unique()],
                            value=list(data['Country'].unique()),
                            clearable=False,
                            multi=True,
                            style={'width': '100%'}
                        )
                    ],
                        style={
                            'display': 'flex',
                            'flexDirection': 'row',
                            'alignItems': 'center',
                            'gap': '8px',
                            'flex': '0 0 1200px',
                            'minWidth': '320px',
                            'maxWidth': '100%'
                        })
                ],
                    style={
                        'display': 'flex',
                        'alignItems': 'flex-start',
                        'gap': '12px',
                        'flexWrap': 'wrap',
                        'padding': '0 12px',
                        'marginTop': '4px'
                    })
            ],
                style={'marginBottom': '18px', 'width': '100%'}
            ),

            # CARDS (total transactions / total inversion)
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.H4("Total Transactions", className="card-title",
                                        style={'marginBottom': '0px', 'fontSize': '35px', 'fontWeight': '700'}),
                                html.H2(id='total-transactions', className="card-text",
                                        style={'fontSize': '28px', 'fontWeight': '700'})
                            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                            html.Div([
                                html.H4("Total Inversion", className="card-title",
                                        style={'marginBottom': '0px', 'fontSize': '35px', 'fontWeight': '700'}),
                                html.H2(id='total-millions', className="card-text",
                                        style={'fontSize': '28px', 'fontWeight': '700'})
                            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
                        ]),
                    ])
                ]), width=4)
            ], style={'marginTop': '5px'}),

            # INDUSTRY CARDS (gráfica horizontal/vertical responsiva generada por callback)
            html.Div([
                html.H3("Overall Money Spent by Industry Sectors",
                        style={'marginBottom': '10px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.Div(id='industry-cards', style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '5px',
                    'width': '100%',
                    'paddingLeft': 0,
                    'paddingRight': 0
                })
            ], style={'marginBottom': '10px'}),
        ],
            style={
                'border': '1px solid #d9d9d9',
                'borderRadius': '10px',
                'padding': '0px 25px',
                'backgroundColor': "#f9f9f9d1",
                'marginBottom': '5px',
                'marginTop': '5px'
            }
        ),  # fin Statistical Overview

        # ===========================
        # SECTION: GEOGRAPHICAL ANALYSIS
        # ===========================
        html.Div([
            html.H2("🗺️ Geographical Analysis", style={'marginBottom': '20px', 'fontSize': '45px', 'fontWeight': '700'}),
            html.Div([
                html.H3("Reported Transactions Map (QUE SE VEAN LAS SUBGRÁFICAS Y LA LEYENDA QUE ES MUY PEQUEÑA)", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Select...........", id='overview-helper-text',
                    style={'textAlign': 'left', 'color': '#000000', 'fontSize': '1.5rem', 'lineHeight': '1.6',
                            'maxWidth': '900px', 'marginTop': '6px', 'marginBottom': '8px', 'padding': '0 12px'}),
                html.Iframe(id='reported-map', style={'width': '100%', 'height': '500px', 'border': '1px solid #ccc', 'borderRadius': '8px'}),
            ], style={'marginBottom': '30px'}),

            html.Div([
                html.H3("Transaction Flux Map", style={'marginBottom': '20px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.P("Select a country to view its transactions with other countries. You can also filter by date and transaction type. Each arrow represents a transaction.",
                    id='flux-description',
                    style={'textAlign': 'left', 'color': '#000000', 'fontSize': '1.5rem', 'lineHeight': '1.6',
                            'maxWidth': '2000px', 'marginTop': '1px', 'marginBottom': '20px', 'padding': '0 12px'}),

                # CONTROLES Date / Transaction Type / Country - alineados en fila
                html.Div([
                    html.Div([
                        html.Label("📅 Date:",
                                style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px', 'marginRight': '12px'}),
                        dcc.DatePickerSingle(
                            id='date-picker',
                            date=data['Date'].min(),
                            display_format='YYYY-MM-DD',
                            min_date_allowed=data['Date'].min(),
                            max_date_allowed=data['Date'].max(),
                            # <-- menos espacio a la derecha y ancho algo menor para no "empujar"
                            style={'marginRight': '6px', 'minWidth': '100px'}
                        ),
                    ],
                    # <-- hago que Date tenga un ancho base fijo similar al del Country selector
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '6px', 'flex': '0 0 320px', 'marginRight': '0px'}),  # <-- CAMBIO

                    html.Div([
                        html.Label("Transaction Type:",
                                style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px', 'marginRight': '12px', 'whiteSpace': 'nowrap'}),
                        dcc.Checklist(
                            id='transaction-checklist',
                            options=[
                                {'label': 'Origin', 'value': 'origin'},
                                {'label': 'Destination', 'value': 'destiny'}
                            ],
                            value=['destiny'],
                            inline=True,
                            inputStyle={'transform': 'scale(1.4)', 'marginRight': '10px', 'verticalAlign': 'middle'},
                            labelStyle={'fontSize': '18px', 'fontWeight': '600', 'marginRight': '18px'},
                            style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}
                        )
                    ],
                    # <-- evitar que el checklist se estire; que ocupe su contenido mínimo
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '6px', 'flex': '0 0 auto', 'marginRight': '0px'}),  # <-- CAMBIO

                    html.Div([
                        html.Label("Country Selection:",
                                style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px', 'lineHeight': '1',
                                        'marginRight': '12px', 'whiteSpace': 'nowrap'}),
                        dcc.Dropdown(
                            id='country-selector',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()] + [{'label': 'ALL', 'value': 'ALL'}],
                            value='USA',
                            clearable=False,
                            style={'width': '100%'}
                        ),
                    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'flex': '0 0 400px', 'minWidth': '320px'}),
                ],
                # <-- CAMBIO: menos gap, items centrados verticalmente y sin tanto wrap
                style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'flexWrap': 'wrap', 'padding': '0 12px',
                    'marginTop': '4px', 'marginBottom': '20px'}),


                # GRAPH wrapper con paddingBottom para ticks
                dcc.Loading(
                    id='loading-arrow-map',
                    children=html.Div(
                        dcc.Graph(id='transaction-arrow-map', style={'width': '100%', 'height': '640px', 'marginLeft': 0, 'paddingLeft': 0}, config={'responsive': True}),
                        style={'paddingBottom': '80px', 'boxSizing': 'border-box'}
                    ),
                    type='graph',
                    color="#8afa7c",
                    fullscreen=False
                )
            ], style={'marginBottom': '40px'}),
        ], style={
            'border': '1px solid #d9d9d9',
            'borderRadius': '10px',
            'padding': '5px 25px',
            'marginBottom': '5px',
            'backgroundColor': '#f9f9f9'
        }),  # fin Geographical Analysis

        # ===========================
        # SECTION: INDUSTRIAL ANALYSIS
        # ===========================
        html.Div([
            html.H2("🏭 Industrial Analysis", style={'marginBottom': '20px', 'fontSize': '45px', 'fontWeight': '700'}),
            html.H3("Source of Transactions", style={'marginBottom': '12px', 'fontSize': '35px', 'fontWeight': '700'}),

            # FILA: Dropdown country + Normalize button (alineados)
            html.Div([
                html.Label("Country Selection:",
                        style={
                            'fontWeight': '700',
                            'marginBottom': '0px',
                            'fontSize': '25px',
                            'lineHeight': '1',
                            'marginRight': '12px',
                            'whiteSpace': 'nowrap'
                        }
                ),

                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                    value='USA',
                    clearable=False,
                    style={'flex': '1 1 auto', 'minWidth': '180px'}
                ),

                dbc.Button(
                    '🔄 Normalize',
                    id='normalize-button',
                    n_clicks=0,
                    style={'flex': '0 0 160px', 'marginLeft': '12px', 'height': '44px', 'whiteSpace': 'nowrap'}
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'width': '100%', 'boxSizing': 'border-box', 'marginBottom': '18px'}),

            # GRAFICO 1: Industry bar chart (IMPORTANTE: id presente)
            dcc.Loading(
                id='loading-industry-bar-chart',
                children=html.Div(
                    dcc.Graph(
                        id='industry-bar-chart',
                        style={'width': '100%', 'height': '48vh', 'minHeight': '420px', 'boxSizing': 'border-box'},
                        config={'responsive': True}
                    ),
                    # <-- AÑADIDO paddingBottom para que la leyenda/ticks no se corten
                    style={'paddingBottom': '80px', 'boxSizing': 'border-box'}
                ),
                type='graph',
                fullscreen=False
            ),

            # Transactions over time controls + graph
            html.Div([
                html.H3("Transactions Over Time", style={'marginBottom': '12px', 'fontSize': '35px', 'fontWeight': '700'}),
                html.Div([
                    html.P(
                            "Explicación.....",
                            id='overview-helper-text-2',
                            style={
                                'textAlign': 'left',
                                'color': '#000000',
                                'fontSize': '1.5rem',
                                'lineHeight': '1.6',
                                'maxWidth': '900px',
                                'marginTop': '6px',
                                'marginBottom': '8px',
                                'padding': '0 12px'
                            }
                        ),
                    html.Div([
                        html.Label("Industry Selection:", style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px'}),
                        dcc.Dropdown(
                            id='industry-dropdown',
                            options=[{'label': industry, 'value': industry} for industry in data['Industry'].unique()],
                            value=data['Industry'].unique().tolist(),
                            multi=True,
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], style={'width': '55%', 'display': 'inline-block', 'paddingRight': '20px', 'boxSizing': 'border-box'}),

                    html.Div([
                        html.Label("Countries Selection:", style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px'}),
                        dcc.Dropdown(
                            id='country-dropdown-multi',
                            options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                            value=['USA'],
                            multi=True,
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], style={'width': '40%', 'display': 'inline-block', 'boxSizing': 'border-box'}),
                ], style={'marginBottom': '16px'}),

                html.Label("Window Size for Moving Average:", style={'fontWeight': '700', 'marginBottom': '0px', 'fontSize': '25px'}),
                dcc.Slider(
                    id='window-size-slider',
                    min=1, max=25, step=1, value=5,
                    marks={i: str(i) for i in range(1, 26, 5)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    updatemode='drag'
                ),

                dcc.Loading(
                    id='loading-transaction-over-time',
                    children=html.Div(
                        dcc.Graph(
                            id='transactions-over-time',
                            style={'width': '100%', 'height': '60vh', 'minHeight': '480px', 'boxSizing': 'border-box'},
                            config={'responsive': True}
                        ),
                        # <-- paddingBottom para ticks/legend
                        style={'paddingBottom': '120px', 'boxSizing': 'border-box'}
                    ),
                    type='graph',
                    fullscreen=False,
                    color="#ff5733",
                    style={'marginTop': '20px'}
                )
            ]),

        ], style={
            'border': '1px solid #d9d9d9',
            'borderRadius': '10px',
            'padding': '25px',
            'backgroundColor': '#f9f9f9',
            'marginBottom': '40px',
            'boxSizing': 'border-box',
            # quitado overflow: hidden para evitar que los plots se corten (leyenda, ticks o subgráficas)
            'overflow': 'visible',
            'width': '100%',
            'maxWidth': '100%'
        }),  # fin Industrial Analysis

        # FOOTER / AUTHORS
        html.Div([
            html.Hr(),
            html.Div([
                html.P("Authors:", style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#666', 'marginBottom': '10px'}),
                html.P("Mario García Berenguer (@Mariogarber) & Eder Tarifa Fernández (@EderTarifa)",
                    style={'textAlign': 'center', 'fontStyle': 'italic', 'color': '#888', 'marginTop': '0px'})
            ])
        ], style={'marginTop': '20px', 'paddingBottom': '40px', 'clear': 'both'}),

    ], style={'fontFamily': 'Arial, sans-serif', 'padding': '30px', 'paddingBottom': '60px'})

    return layout
