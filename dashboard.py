import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

import os

from functions.layout import create_layout_v2
from functions.data_processing import DataManager
from functions.graph import make_info_folium_map, make_transaction_arrow_map, make_stacked_illegal_legal, make_transaction_over_time

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
    app.run(host='0.0.0.0', port=port)