import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc

import os

from functions.layout import create_layout_v2
from functions.data_processing import DataManager
from functions.graph import make_info_folium_map, make_transaction_arrow_map, make_stacked_illegal_legal, make_cards_for_industries, make_transaction_over_time

DATA_PROCESSOR = DataManager()
data = DATA_PROCESSOR.get_data()
gdf = DATA_PROCESSOR.geodata
iso_a3= DATA_PROCESSOR.iso_a3_dict

FOLIUM_MAP_INFO = DATA_PROCESSOR.set_folium_data()
_ = DATA_PROCESSOR.set_arrow_data()

MIN_DATE = data['Date'].min()

app = dash.Dash(__name__)
app.layout = create_layout_v2(data)

@app.callback(
    Output('total-transactions', 'children'),
    Output('total-millions', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('country-dropdown-overview', 'value')
)
def update_overview_cards(start_date, end_date, selected_countries):
    filtered_data = DATA_PROCESSOR.filter_data_by_date_and_country(start_date, end_date, selected_countries)
    total_transactions = len(filtered_data)
    total_millions = filtered_data['Amount (USD)'].sum() / 1_000_000
    return f"{total_transactions:,}", f"${total_millions:,.2f}M"

@app.callback(
    Output('industry-cards', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('country-dropdown-overview', 'value')
)
def update_industry_cards(start_date, end_date, selected_countries):
    filtered_data = DATA_PROCESSOR.filter_data_by_date_and_country(start_date, end_date, selected_countries)
    total_industry_amount = DATA_PROCESSOR.data.groupby('Industry')['Amount (USD)'].sum().sum()

    total_amount = filtered_data['Amount (USD)'].sum()

    card_components = make_cards_for_industries(filtered_data)
    
    # Add Total card
    total_card = dbc.Card([
        dbc.CardBody([
            html.H3(
                "Total", 
                className="card-title", 
                style={
                    'color': '#dc3545', 
                    'margin': '10px 0',
                    'fontWeight': 'bold',
                    'fontSize': '1.1rem',
                    'letterSpacing': '0.5px'
                }
            ),
            html.H2(
                f"${total_amount/1_000_000:,.2f}M", 
                className="card-text", 
                style={
                    'color': '#dc3545', 
                    'margin': '0 0 20px 0',
                    'fontWeight': '700',
                    'fontSize': '1.6rem',
                    'textShadow': '1px 1px 2px rgba(0,0,0,0.1)'
                }
            ),
            html.H2(
                f"{total_amount/total_industry_amount:,.5f}%", 
                className="card-text", 
                style={
                    'color': '#dc3545', 
                    'margin': '0 0 20px 0',
                    'fontWeight': '700',
                    'fontSize': f'{1.6 + 1 *(total_amount/total_industry_amount)}rem',
                    'textShadow': '1px 1px 2px rgba(0,0,0,0.1)'
                }
            ),
            html.H3(
                "Percentage of Total Amount", 
                className="card-title", 
                style={
                    'color': '#dc3545', 
                    'margin': '10px 0',
                    'fontWeight': 'bold',
                    'fontSize': '1.1rem',
                    'letterSpacing': '0.5px'
                }
            ),
        ],
        style={
            'padding': '35px',
            'textAlign': 'center'
        }
        )
    ], 
    style={
        'margin': '20px',
        'borderRadius': '20px',
        'boxShadow': '0 12px 24px rgba(0,0,0,0.15)',
        'minWidth': '300px',
        'minHeight': '100px',
        'background': 'linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%)',
        'border': '2px solid #dc3545',
        'transition': 'all 0.3s ease-in-out',
        'cursor': 'pointer'
    },
    className="h-100 shadow-lg"
    )
    
    card_components.append(total_card)

    rows = html.Div(
    card_components,
    style={
        'display': 'flex', 
        'gap': '40px', 
        'justifyContent': 'center',
        'flexWrap': 'wrap',
        'padding': '30px'
    }
    )

    return rows

@app.callback(
    Output('reported-map', 'srcDoc'),
    Input('reported-map', 'id')  # Dummy input to trigger the callback once
)
def update_folium_map(_):
    folium_map = make_info_folium_map(**FOLIUM_MAP_INFO)
    return folium_map

@app.callback(
    Output('transaction-arrow-map', 'figure'),
    Input('date-picker', 'date'),
    Input('transaction-checklist', 'value'),
    Input('country-selector', 'value')
)
def update_arrow_map(selected_date, arrow_options, selected_country):
    selected_date = pd.to_datetime(selected_date).date()
    if selected_date is None or selected_date < MIN_DATE:
        selected_date = MIN_DATE
    flows_info = DATA_PROCESSOR.filter_flows(arrow_options, selected_country, selected_date)
    fig, _ = make_transaction_arrow_map(**flows_info)
    return fig

@app.callback(
    Output('industry-bar-chart', 'figure'),
    Input('country-dropdown', 'value'),
    Input('normalize-button', 'n_clicks')
)
def update_stacked_bar_chart(selected_country, normalize_clicks, dataset=data):
    fig = make_stacked_illegal_legal(selected_country=selected_country, normalize_clicks=normalize_clicks, dataset=dataset)
    return fig

@app.callback(
    Output('transactions-over-time', 'figure'),
    Input('industry-dropdown', 'value'),
    Input('country-dropdown-multi', 'value'),
    Input('window-size-slider', 'value'),
    Input('date-picker', 'date')
)
def update_transaction_information(selected_industries, country_selected, window_size, selected_date, dataset=data, iso_a3_dict=iso_a3):
    if not selected_industries:
        selected_industries = dataset['Industry'].unique().tolist()
    if not country_selected:
        country_selected = dataset['Country'].unique().tolist()
    selected_date = pd.to_datetime(selected_date).date()
    fig = make_transaction_over_time(dataset=dataset, iso_a3_dict=iso_a3_dict, selected_industries=selected_industries, 
                                     country_selected=country_selected, window_size=window_size, selected_date=selected_date)
    return fig

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)