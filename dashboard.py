import dash
from dash import dcc, html, no_update, callback_context
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_bootstrap_components as dbc
import copy
import plotly.graph_objects as go

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

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.layout = create_layout_v2(data)

@app.callback(
    Output('normalize-button', 'children'),
    Output('normalize-button', 'color'),
    Input('normalize-button', 'n_clicks')
)
def toggle_normalize_button(n_clicks):
    if not n_clicks:
        n_clicks = 0
    label = "🔄 Denormalize" if (n_clicks % 2 == 1) else "🔄 Normalize"
    color = "success" if (n_clicks % 2 == 1) else "primary"
    return label, color

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

    graph_component = make_cards_for_industries(
        filtered_data,
        palette='Plotly',
        mode='categorical',
        color_map=globals().get('color_map_industries', None),
        top_n=None
    )

    # Si graph_component ya es un Div que envuelve el dcc.Graph, lo devolvemos tal cual pero
    # nos aseguramos de no limitar el ancho con maxWidth. Si es otra cosa, lo envolvemos.
    if isinstance(graph_component, (html.Div, dbc.Card, dbc.Row)):
        return graph_component  # ya debería tener style width:100% en su interior
    else:
        return html.Div(
            graph_component,
            style={
                'padding': '10px 0',
                'width': '90%',
                'maxWidth': '100%',
                'margin': '0',
                'boxSizing': 'border-box'
            }
        )


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
    Input('visible-industries-store', 'data'),
    Input('country-dropdown', 'value'),
    Input('normalize-button', 'n_clicks'),
    prevent_initial_call=False
)
def build_industry_fig(visible_industries, selected_country, normalize_clicks):
    """
    Reconstruye la figura usando únicamente las industrias en visible_industries.
    De esta forma al ocultar una industria con la leyenda, la figura se recompone sin dejar huecos.
    """
    # Si no vienen industrias visibles, devolvemos figura vacía con un texto
    if not visible_industries:
        fig_empty = go.Figure()
        fig_empty.update_layout(
            template='plotly_white',
            annotations=[dict(text="No industry selected", showarrow=False, x=0.5, y=0.5, xref='paper', yref='paper')],
            margin=dict(l=8, r=20, t=20, b=40)
        )
        return fig_empty

    # Filtrar dataset por país (si tu DataManager tiene un filtro mejor úsalo):
    # Asegúrate que selected_country es coherente (puede ser lista o 'ALL').
    if selected_country == 'ALL' or selected_country is None:
        dataset_country = data.copy()
    else:
        # Si tu country-dropdown es multi, ajusta la condición
        if isinstance(selected_country, list):
            dataset_country = data[data['Country'].isin(selected_country)]
        else:
            dataset_country = data[data['Country'] == selected_country]

    # Ahora filtramos por las industrias visibles guardadas en el store
    dataset_filtered = dataset_country[dataset_country['Industry'].isin(visible_industries)]

    # Llamamos a tu función de construcción de figura pasando el dataset filtrado.
    # Si make_stacked_illegal_legal acepta dataset param (como en tu código), lo usamos:
    fig = make_stacked_illegal_legal(selected_country=selected_country,
                                    normalize_clicks=normalize_clicks,
                                    dataset=dataset_filtered)

    # Ajustes visuales finales (asegurar que no deja gap por margen Plotly)
    # Ajusta left_margin si tus labels son largas
    left_margin = 40
    fig.update_layout(margin=dict(l=left_margin, r=20, t=20, b=40), yaxis=dict(automargin=True))

    return fig

''''''
@app.callback(
    Output('visible-industries-store', 'data'),
    Input('industry-bar-chart', 'restyleData'),
    State('visible-industries-store', 'data'),
    State('industry-bar-chart', 'figure'),
    prevent_initial_call=True
)
def sync_visible_store(restyle_data, current_store, current_fig):
    """
    Interpreta restyleData y actualiza el dcc.Store con la lista de industrias VISIBLES.
    IMPORTANTE: aplicamos los cambios de restyleData sobre una copia de current_fig
    (porque current_fig puede no haber sido actualizado todavía por el cliente).
    """
    if not restyle_data or not current_fig:
        return no_update

    # copia de la figura para aplicar los cambios
    fig = copy.deepcopy(current_fig)

    # restyle_data suele tener forma: [changes_dict, trace_indices]
    # ejemplo: [{'visible': ['legendonly']}, [2]]
    try:
        changes = restyle_data[0]
        idxs = restyle_data[1] if len(restyle_data) > 1 else []
    except Exception:
        # formato inesperado -> no actualizar
        return no_update

    # Si el cambio incluye visibilidad, aplícalo sobre la copia de la figura
    if isinstance(changes, dict) and 'visible' in changes:
        new_vis = changes['visible']
        # new_vis suele ser lista con 1 elemento (p. ej. ['legendonly'] o [True])
        for i in idxs:
            if 0 <= i < len(fig.get('data', [])):
                val = new_vis[0] if isinstance(new_vis, (list, tuple)) else new_vis
                fig['data'][i]['visible'] = val

    # --- Ahora construimos la lista de industrias visibles (post-cambio) ---
    visible = []
    for trace in fig.get('data', []):
        vis = trace.get('visible', True)
        if vis != 'legendonly':
            # trace.name debe ser el nombre de la industria (si usas color='Industry' en px)
            name = trace.get('name')
            if name:
                visible.append(name)

    # Si no cambió el store, no actualizar
    if current_store == visible:
        return no_update

    return visible

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