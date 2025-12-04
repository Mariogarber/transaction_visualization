import plotly.graph_objects as go
import random
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import folium
import io
import base64
import matplotlib
from dash import dcc, html
import dash_bootstrap_components as dbc
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px



#create a dict to map each coutry to a color
country_color = {
    'USA': 'blue',
    'ZAF': 'orange',
    'CHE': 'green',
    'RUS': 'red',
    'BRA': "#7FE956",
    'GBR': 'brown',
    'IND': 'pink',
    'CHN': 'gray',
    'SGP': 'cyan',
    'ARE': 'magenta'
}

country_name_color = {
    'USA': 'blue',
    'South Africa': 'orange',
    'Switzerland': 'green',
    'Russia': 'red',
    'Brazil': "#7FE956",
    'UK': 'brown',
    'India': 'pink',
    'China': 'gray',
    'Singapore': 'cyan',
    'UAE': 'magenta'
}

colorscale = [
    [0.0, '#FFFFB2'],   # light yellow
    [0.25, '#FECC5C'],  # yellow-orange
    [0.5, '#FD8D3C'],   # orange
    [0.75, '#F03B20'],  # red-orange
    [1.0, '#BD0026']    # dark red
]

color_transaction_type = {
    "Offshore Transfer": "#AEC6CF",  # pastel blue
    "Cash Withdrawal": "#FFB347",      # pastel orange
    "Cryptocurrency": "#77DD77",       # pastel green
    "Stocks Transfer": "#FFB6C1",      # pastel pink
    "Property Purchase": "#CBAACB"     # pastel purple
}

color_map_industries = {
    'Arms Trade': "#ed5903",
    'Construction': "#2eaf4d",
    'Luxury Goods': '#ffc107',
    'Casinos': '#17a2b8',
    'Oil & Gas': "#8550e8",
    'Real Estate': "#f23f92",
    'Finance': "#c5e03eb3",
}

def get_color(amount, min_amt, max_amt):
    # Normalize amount to [0, 1] and map to colorscale
    if max_amt == min_amt:
        idx = 0
    else:
        idx = int((amount - min_amt) / (max_amt - min_amt) * (len(colorscale) - 1))
    return colorscale[idx][1]


def _normalize_color_for_plotly(color):
    """
    Acepta: '#RRGGBBAA', '#RRGGBB', '#RGB', 'rgb(...)', 'rgba(...)', nombres css.
    Devuelve: color en formato aceptado por Plotly: '#RRGGBB' o 'rgba(r,g,b,a)' o la cadena original.
    """
    if color is None:
        return None
    if not isinstance(color, str):
        return color

    c = color.strip()
    # #RRGGBBAA -> rgba(...)
    if c.startswith('#') and len(c) == 9:  # incluyendo '#'
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            a = int(c[7:9], 16) / 255.0
            return f'rgba({r},{g},{b},{a:.3f})'
        except Exception:
            return c  # fallback, devolver tal cual
    # short hex #RGB -> expand to #RRGGBB
    if c.startswith('#') and len(c) == 4:
        r = c[1]*2
        g = c[2]*2
        b = c[3]*2
        return f'#{r}{g}{b}'
    # #RRGGBB -> ok
    if c.startswith('#') and len(c) == 7:
        return c
    # already rgb(...) or rgba(...) or named color -> return as is
    return c

def make_cards_for_industries(filtered_data,
                              palette='Viridis',
                              mode='categorical',
                              height=500,
                              color_map=None,
                              top_n=None,
                              hide_legend=True):
    """
    Gráfico de barras VERTICALES: muestra Amount_M por Industry.
    - Empieza el eje Y en ~95% del mínimo mostrado (si minimum>0).
    - Textos encima de las barras con formato $X.YY M.
    - Ocupa el 90% del ancho del contenedor y queda centrado.
    """
    if filtered_data is None or filtered_data.empty:
        return html.Div("No hay transacciones en el rango/país seleccionado.", style={'textAlign': 'center', 'color': '#666'})

    industry_sums = (filtered_data
                     .groupby('Industry', as_index=False)['Amount (USD)']
                     .sum()
                     .rename(columns={'Amount (USD)': 'Amount_USD'}))

    industry_elements = list(industry_sums.set_index('Industry')['Amount_USD'].items())
    industry_elements_ordered = sorted(industry_elements, key=lambda x: x[1])
    ordered_industries = [ind for ind, amt in industry_elements_ordered]
    industry_sums = industry_sums.set_index('Industry').reindex(ordered_industries).reset_index()

    if top_n:
        industry_sums = industry_sums.sort_values('Amount_USD', ascending=False).head(top_n).sort_values('Amount_USD', ascending=True)

    industry_sums['Amount_M'] = industry_sums['Amount_USD'] / 1_000_000
    n = len(industry_sums)
    if n == 0:
        return html.Div("No hay industrias con datos.", style={'textAlign': 'center', 'color': '#666'})

    # Altura dinámica (más industrias => más alto)
    if height is None:
        height = max(300, 48 * n + 120)
    else:
        height = max(height, 48 * n + 120)

    if color_map is None:
        color_map = globals().get('color_map_industries', None)

    def _normalize_map(cm):
        if not cm:
            return None
        return {k: _normalize_color_for_plotly(v) for k, v in cm.items()}

    color_map_processed = _normalize_map(color_map)

    # Selección de colores (categorical o continuous)
    if mode == 'continuous':
        palette_list = getattr(px.colors.sequential, palette, px.colors.sequential.Viridis)
        palette_list = [_normalize_color_for_plotly(c) for c in palette_list]
        fig = px.bar(industry_sums,
                     x='Industry',
                     y='Amount_M',
                     color='Amount_M',
                     color_continuous_scale=palette_list,
                     labels={'Amount_M': 'Amount (USD) — Millions', 'Industry': 'Industry'},
                     template='plotly_white',
                     height=height)
        fig.update_layout(coloraxis_showscale=False)
    else:
        if color_map_processed:
            fig = px.bar(industry_sums,
                         x='Industry',
                         y='Amount_M',
                         color='Industry',
                         color_discrete_map=color_map_processed,
                         labels={'Amount_M': 'Amount (USD) — Millions', 'Industry': 'Industry'},
                         template='plotly_white',
                         height=height)
        else:
            palette_seq = getattr(px.colors.qualitative, palette, px.colors.qualitative.Plotly)
            palette_seq = [_normalize_color_for_plotly(c) for c in palette_seq]
            fig = px.bar(industry_sums,
                         x='Industry',
                         y='Amount_M',
                         color='Industry',
                         color_discrete_sequence=palette_seq,
                         labels={'Amount_M': 'Amount (USD) — Millions', 'Industry': 'Industry'},
                         template='plotly_white',
                         height=height)

    # Texto encima de la barra (y = valor) -> más grande
    fig.update_traces(texttemplate='$%{y:,.0f}M', textposition='outside', cliponaxis=False)

    # ----- Calcular rango Y dinámico (empieza en 95% del mínimo mostrado) -----
    try:
        y_min = float(industry_sums['Amount_M'].min())
        y_max = float(industry_sums['Amount_M'].max())
    except Exception:
        y_min = None
        y_max = None

    if y_min is None or np.isnan(y_min) or y_max is None or np.isnan(y_max):
        y_range = None
    else:
        if y_min > 0:
            start = y_min * 0.95
        else:
            start = 0.0

        if y_max <= y_min:
            if y_max == 0:
                end = start + 1.0
            else:
                end = y_max * 1.05
        else:
            end = y_max * 1.05

        if start >= end:
            start = max(0.0, y_min - abs(0.1 * y_min))
            if start >= end:
                start = max(0.0, y_min * 0.95)

        y_range = [start, end]

    # ----- Parámetros visuales ajustables (aquì puedes tocar los tamaños) -----
    # He aumentado los tamaños de fuentes aquí:
    title_font_size = 30          # tamaño del título del gráfico
    axis_title_font_size = 18     # tamaño de los títulos de eje (X/Y)
    x_tick_font_size = 18         # <-- modificado: tamaño de los nombres de las columnas (ticks X)
    y_tick_font_size = 16         # tamaño de ticks Y
    numbers_font_size = 16        # <-- modificado: tamaño de los números encima de barras

    # Margenes para dar espacio al título del eje y a labels rotadas
    left_margin = 80
    right_margin = 80
    top_margin = 60
    bottom_margin = 60  # <-- aumentado para dejar espacio a etiquetas X rotadas y al título X

    # espaciar barras (más ancho -> barras más delgadas a menos bargap pequeño)
    bargap_value = 0.15
    bargroupgap_value = 0.02

    # Rotación etiquetas X si muchas categorías (puedes dejar 0 si no quieres rotación)
    x_tickangle = -35

    # Aplicar layout y ejes
    yaxis_dict = dict(title='Amount (USD) — Millions', tickformat=',.0f')
    if y_range is not None:
        yaxis_dict['range'] = y_range

    # Usamos update_layout y update_xaxes/update_yaxes para controlar titulitos y separación
    fig.update_layout(
        autosize=True,
        height=height,
        margin=dict(l=left_margin, r=right_margin, t=top_margin, b=bottom_margin),
        xaxis=dict(title='', tickangle=x_tickangle, tickfont=dict(size=x_tick_font_size), automargin=True),
        yaxis=yaxis_dict,
        template='plotly_white',
        bargap=bargap_value,
        bargroupgap=bargroupgap_value    
        )

    fig.update_xaxes(tickangle=0)

    # Forzamos responsive en traces y texto
    fig.update_traces(textfont=dict(size=numbers_font_size), selector=dict(type='bar'))

    # tamaño de ticks y textos
    fig.update_xaxes(tickfont=dict(size=x_tick_font_size, family="Arial"))
    fig.update_yaxes(tickfont=dict(size=y_tick_font_size, family="Arial"))
    fig.update_traces(textfont=dict(size=numbers_font_size))

    # Si el usuario quiere ocultar la leyenda:
    if hide_legend:
        fig.update_layout(showlegend=False)
        fig.update_traces(showlegend=False)

    # Forzar que la gráfica se adapte al ancho del contenedor en Dash y ocupe 90% (centrada)
    graph = dcc.Graph(
        figure=fig,
        config={'displayModeBar': False, 'responsive': True},
        style={'width': '90%', 'height': f'{height}px', 'margin': '0 auto', 'display': 'block'}  # <-- modificado a 90% y centrado
    )

    return html.Div(
        graph,
        style={
            'maxWidth': '100%',
            'paddingLeft': 0,
            'paddingRight': 0,
            'width': '100%',   # el wrapper sigue 100% del contenedor; el Graph ocupa 90% dentro de él
            'textAlign': 'center'  # opcional: centra el graph dentro del div
        }
    )


def make_industry_bar_figure(dataset, visible_industries=None, palette='Plotly', height_per_item=48, min_height=420):
    df = dataset.copy()
    if 'Industry' not in df.columns or 'Amount (USD)' not in df.columns:
        return go.Figure()

    df['Industry'] = df['Industry'].astype(str).str.strip()
    sums = df.groupby('Industry', as_index=False)['Amount (USD)'].sum().rename(columns={'Amount (USD)': 'Amount_USD'})
    if sums.empty:
        return go.Figure()

    sums['Amount_M'] = sums['Amount_USD'] / 1_000_000.0

    if visible_industries:
        visible_norm = [v.strip() for v in visible_industries]
        sums = sums[sums['Industry'].isin(visible_norm)]

    sums = sums.sort_values('Amount_M', ascending=True)
    n = len(sums)
    height = max(min_height, int(n * height_per_item + 120))

    palette_seq = getattr(px.colors.qualitative, palette, px.colors.qualitative.Plotly)
    colors = [palette_seq[i % len(palette_seq)] for i in range(n)]

    fig = go.Figure()
    for i, row in sums.reset_index().iterrows():
        ind = row['Industry']
        amt_m = row['Amount_M']
        fig.add_trace(go.Bar(
            x=[amt_m],
            y=[ind],
            orientation='h',
            name=ind,
            marker=dict(color=colors[i], line=dict(width=0)),
            text=f"${amt_m:,.2f}M",
            textposition='outside',             # texto fuera al final de cada barra
            textfont=dict(size=11, color='black'),
            hovertemplate=f"{ind}<br>Amount: $%{{x:,.2f}}M<extra></extra>",
            showlegend=False                    # ocultar leyenda
        ))

    fig.update_layout(
        template='plotly_white',
        height=height,
        margin=dict(l=8, r=140, t=40, b=40),  # r aumentado para evitar recorte de texto
        showlegend=False
    )
    fig.update_yaxes(autorange='reversed')  # mantiene el mismo orden visual

    # Asegurarnos que si por alguna razón textposition no se aplica, lo forzamos:
    fig.update_traces(cliponaxis=False)

    return fig





# Folium map with pie charts and bar charts as popups on country centroids

def make_info_folium_map(clean_data_illegal, geo_data, map_illegal_data, map_transactions_data):

    map = folium.Map(location=[20, 0], zoom_start=2)

    # Choropleth layer for total illegal amount by country

    folium.Choropleth(
        geo_data=geo_data[['admin', 'geometry']],
        name='choropleth',
        data=clean_data_illegal.groupby('Country')['Amount (USD)'].sum() / 1e6,
        columns=['admin', 'Illegal Ratio'],
        key_on='feature.properties.admin',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Total Illegal Amount (Millions USD)',
    ).add_to(map)

    # Centroid markers with pie charts of illegal vs legal transactions

    fg_markers = folium.FeatureGroup(name="centroid_markers_illegal")
    for country, ratio in map_illegal_data.items():
        geometry = geo_data[geo_data['admin'] == country].geometry
        if geometry.empty:
            continue
        centroid = geometry.values[0].centroid

        fig, ax = plt.subplots(figsize=(2, 2), dpi=150)
        ax.pie([ratio, 1 - ratio], colors=[colorscale[int(ratio * (len(colorscale) - 1))][1], "#FF6A6A"], startangle=90)
        ax.axis('equal')
        ax.set_title(f"{country}\nIllegal Ratio: {ratio:.2%}", fontsize=8)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')  # guarda como PNG in-memory
        plt.close(fig)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        html = f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{img_base64}" style="max-width:100%; height:auto;" />
        </div>
        """
        iframe_popup = folium.IFrame(html=html, width=150, height=170)
        popup = folium.Popup(iframe_popup, max_width=300)

        folium.Marker(
            location=[centroid.y, centroid.x],
            radius=5 + ratio * 20,
            popup=popup,
            color='blue',
            
        ).add_to(fg_markers)

    fg_markers.add_to(map)

    # Centroid markers with bar charts of transaction types

    fg_markers = folium.FeatureGroup(name="centroid_markers_transactions")
    for country, ratio in map_illegal_data.items():
        geometry = geo_data[geo_data['admin'] == country].geometry
        if geometry.empty:
            continue
        centroid = geometry.values[0].centroid

        fig, ax = plt.subplots(figsize=(2, 2), dpi=150)
        ax.bar(map_transactions_data[country].keys(), map_transactions_data[country].values(), color=[color_transaction_type.get(txn_type, "#FFFFFF") for txn_type in map_transactions_data[country].keys()])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_title(f"Transactions in {country}", fontsize=8)
        ax.set_xticklabels(map_transactions_data[country].keys(), rotation=45, fontsize=8)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')  # guarda como PNG in-memory
        plt.close(fig)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        html = f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{img_base64}" style="max-width:100%; height:auto;" />
        </div>
        """
        iframe_popup = folium.IFrame(html=html, width=150, height=170)
        popup = folium.Popup(iframe_popup, max_width=300)

        folium.Marker(
            location=[centroid.y, centroid.x],
            radius=5 + ratio * 20,
            popup=popup,
            color='blue',
            
        ).add_to(fg_markers)

    fg_markers.add_to(map)
    
    folium.LayerControl().add_to(map)

    return map._repr_html_()

# Map with arrows showing transactions between countries

def make_transaction_arrow_map(flows, gdf_countries, selected_date, total, min_amt, max_amt, show_arrows):

    fig = go.Figure()

    # --- Normalizar 'total' a un dict iso -> numeric_value (robusto para dict/Series/ndarray) ---
    total_map = {}
    try:
        # pandas Series o dict soportan .items()
        for k, v in (total.items() if hasattr(total, 'items') else enumerate(total)):
            # si enumerate returned tuples (index, value) y keys are numeric indices, lo convertimos más abajo
            total_map[k] = v
    except Exception:
        # fallback: si total tiene 'index' y soporta acceso por index (pandas), usarlo
        try:
            if hasattr(total, 'index'):
                for k in total.index:
                    total_map[k] = total[k]
        except Exception:
            # si total es un simple array de valores sin claves ISO, lo dejamos vacío
            total_map = {}

    # Si total era una lista/ndarray sin claves ISO, intentar reconocer iso desde gdf_countries (no garantizado)
    # (normalmente total debe venir como dict o pd.Series con índices iso_a3)
    if not total_map and isinstance(total, (list, tuple, np.ndarray)):
        # intentar mapear por orden si gdf_countries tiene los mismos isos en el mismo orden (raro)
        try:
            isos = list(gdf_countries['iso_a3'].values)
            for i, val in enumerate(total):
                if i < len(isos):
                    total_map[isos[i]] = val
        except Exception:
            total_map = {}

    # --- Preparar arrays para la choropleth ---
    locations = []
    z_values = []
    text_admins = []
    for iso, amt in total_map.items():
        # asegurarse que iso esté en gdf_countries para título limpio; si no, usar iso crudo
        locations.append(iso)
        # convertir amt a float si puede (evitar strings)
        try:
            z_values.append(float(amt))
        except Exception:
            z_values.append(0.0)
        if iso in gdf_countries['iso_a3'].values:
            text_admins.append(gdf_countries.set_index('iso_a3').loc[iso, 'admin'])
        else:
            text_admins.append(iso)

    # Añadir choropleth solo si tenemos datos numéricos
    if locations and any([v is not None for v in z_values]):
        # elige 1 o 2 decimales
        decimals = 1  # pon 2 si quieres dos decimales

        # convertir z_values a MILLIONS para la colorbar y hover
        z_values_m = [float(v) / 1e6 for v in z_values]

        # opcional: adaptar min/max si los tienes en USD
        zmin_m = (min_amt / 1e6) if (min_amt is not None) else None
        zmax_m = (max_amt / 1e6) if (max_amt is not None) else None

        fig.add_trace(go.Choropleth(
            locations=locations,
            z=z_values_m,                      # ahora en millones
            text=text_admins,
            colorscale=[c[1] for c in colorscale],
            autocolorscale=False,
            marker_line_color='white',
            zmin=zmin_m,
            zmax=zmax_m,
            colorbar=dict(
                title=dict(text="<b>Flow Amount (Millions USD)</b>", font=dict(size=15, color="#000000")),
                thickness=15,
                len=0.65,
                x=0.92,
                y=0.98,
                yanchor='top',
                outlinewidth=0,
                # tickformat: coma separador de miles + N decimales -> ",.1f" o ",.2f"
                tickformat=f",.{decimals}f"
            ),
            hoverinfo='text',
            # hovertemplate: muestra z ya en millones con N decimales
            hovertemplate=f'%{{text}}<br>Flow Amount: %{{z:,.{decimals}f}} Millions (USD)<extra></extra>',
            geo='geo',
            showscale=True,
            showlegend=False
        ))


        # Ajusta margenes para que la colorbar no tape ni se corte
        fig.update_layout(
            margin=dict(l=0, r=170, t=30, b=0),  # aumentar r si la barra se corta
            # leyenda ya la tienes personalizada; mantenemos clickmode none si quieres:
            clickmode='none'
        )

    # --- Add arrows for flows (no legend) ---
    traces = []
    for _, r in flows.iterrows():
        traces.append(go.Scattergeo(
            lon=[r['o_lon'], r['d_lon'] + random.uniform(-1.5, 1.5)],
            lat=[r['o_lat'], r['d_lat'] + random.uniform(-1.5, 1.5)],
            mode='lines+markers',
            line=dict(width=1 + r['amount'] / 1000000, color=country_color.get(r['origin_iso_a3'], 'black')),
            marker=dict(
                size=[0, 8 + r['amount'] / 500000],
                symbol=['circle', 'triangle-up'],
                color=['blue', country_color.get(r['origin_iso_a3'], 'black')],
                line=dict(width=[0, 0])
            ),
            opacity=0.7,
            hoverinfo='text',
            text=[
                f"Origin: {r['origin_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['origin_iso_a3'], 'admin']})<br>"
                f"Destination: {r['dest_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['dest_iso_a3'], 'admin']})<br>"
                f"Flow: -{r['amount']/1e6:.1f} Millions (USD)",
                f"Origin: {r['origin_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['origin_iso_a3'], 'admin']})<br>"
                f"Destination: {r['dest_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['dest_iso_a3'], 'admin']})<br>"
                f"Flow: +{r['amount']/1e6:.1f} Millions (USD)"
            ],
            showlegend=False

        ))


    if show_arrows:
        for trace in traces:
            fig.add_trace(trace)

    # --- Leyenda dinámica: solo para los ISOs que aparecen en 'flows' (origen o destino) ---
    # Recolectamos ISOs desde las columnas típicas si existen
    isos_present = set()
    possible_iso_cols = ['origin_iso_a3', 'origin', 'o_iso', 'o_iso_a3', 'dest_iso_a3', 'dest', 'd_iso', 'd_iso_a3']
    for col in possible_iso_cols:
        if col in flows.columns:
            isos_present.update([v for v in flows[col].dropna().unique()])

    # Construimos legend_traces únicamente para los isos presentes
    legend_traces = []
    for iso in sorted(isos_present):
        if not iso:
            continue
        # intenta resolver nombre administrable (admin) desde gdf_countries, sino usar el iso tal cual
        try:
            admin_name = gdf_countries.set_index('iso_a3').loc[iso, 'admin'] if (('iso_a3' in gdf_countries.columns) and (iso in gdf_countries['iso_a3'].values)) else iso
        except Exception:
            admin_name = iso

        # color preferente desde country_color (mapa de ISOs), fallback a country_name_color o 'black'
        color = country_color.get(iso, None) or country_name_color.get(admin_name, None) or 'black'

        legend_traces.append(go.Scattergeo(
            lon=[None], lat=[None],
            mode='markers',
            marker=dict(size=12, color=color),
            name=admin_name,
            text=f"Send by {admin_name}",
            showlegend=True
        ))

    # Añadimos las trazas de leyenda (si show_arrows activado mantenemos la condición original para añadir legend_traces)
    if show_arrows:
        for trace in legend_traces:
            fig.add_trace(trace)

    # --- Layout: leyenda con título ("LEYENDA") y no interactiva ---
    fig.update_layout(
        legend=dict(
            title=dict(text="<b>Arrow legend (origin country)</b>", font=dict(size=15, color="#000000")),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.85)",
            itemclick=False,
            itemdoubleclick=False,
            traceorder='normal'
        ),
        clickmode='none'
    )

    # --- Geo layout ---
    fig.update_geos(
        projection_type='natural earth',
        showcountries=True,
        showcoastlines=True,
        showland=True,
        showocean=True,
        showlakes=True,
        oceancolor="#82C0FF",
        lakecolor="#82C0FF",
        landcolor="#C2A580",
        coastlinecolor="#A0A0A0",
        resolution=110
    )

    return fig, flows


# Stacked Bar Charts with legal vs illegal transactions by industry and country

def make_stacked_illegal_legal(selected_country, normalize_clicks, dataset):
    # Filtrado y conversión a millones
    filtered = dataset[dataset['Country'] == selected_country].copy()
    if filtered.empty:
        # Figura vacía amigable si no hay datos
        fig_empty = make_subplots(rows=1, cols=2, subplot_titles=['Transaction Count', 'Amount (Millions USD)'])
        fig_empty.update_layout(template='plotly_white')
        return fig_empty

    filtered['Amount (USD)'] = filtered['Amount (USD)'] / 1e6

    # Agrupar por Industry y Source of Money → obtener matrix Industry x {Illegal, Legal}
    # Para counts y amounts (usar unstack para alinear industrias y rellenar con 0 donde falte)
    counts = (filtered
              .groupby(['Industry', 'Source of Money'])
              .size()
              .unstack(fill_value=0))

    amounts = (filtered
               .groupby(['Industry', 'Source of Money'])['Amount (USD)']
               .sum()
               .unstack(fill_value=0))

    # Asegurarnos columnas existan y nombrarlas consistentemente
    for col in ['Illegal', 'Legal']:
        if col not in counts.columns:
            counts[col] = 0
        if col not in amounts.columns:
            amounts[col] = 0

    # Orden consistente por industry
    counts = counts.reset_index().sort_values('Industry')
    amounts = amounts.reset_index().sort_values('Industry')

    # Rename para claridad
    counts = counts.rename(columns={'Illegal': 'Illegal Transaction Count', 'Legal': 'Legal Transaction Count'})
    amounts = amounts.rename(columns={'Illegal': 'Illegal Amount (Millions USD)', 'Legal': 'Legal Amount (Millions USD)'})

    # Normalización opcional (fila a fila) evitando division por cero
    suffix = ""
    if normalize_clicks % 2 == 1:
        suffix = " (Normalized)"
        # Counts normalization
        total_counts = counts['Illegal Transaction Count'] + counts['Legal Transaction Count']
        # evitar division por cero: si total_counts==0 -> dejar 0
        counts['Illegal Transaction Count'] = np.where(total_counts > 0,
                                                      counts['Illegal Transaction Count'] / total_counts,
                                                      0)
        counts['Legal Transaction Count'] = np.where(total_counts > 0,
                                                    counts['Legal Transaction Count'] / total_counts,
                                                    0)
        # Amounts normalization
        total_amounts = amounts['Illegal Amount (Millions USD)'] + amounts['Legal Amount (Millions USD)']
        amounts['Illegal Amount (Millions USD)'] = np.where(total_amounts > 0,
                                                           amounts['Illegal Amount (Millions USD)'] / total_amounts,
                                                           0)
        amounts['Legal Amount (Millions USD)'] = np.where(total_amounts > 0,
                                                         amounts['Legal Amount (Millions USD)'] / total_amounts,
                                                         0)

    # Construir subplots
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['Transaction Count', 'Amount (Millions USD)'],
        shared_yaxes=False
    )

    # Colores (mantengo tus colores)
    illegal_color = "#FF4747"
    legal_color = "#77DD77"

    # Añadir traces en el mismo orden de industries (counts)
    fig.add_trace(go.Bar(
        x=counts['Industry'],
        y=counts['Illegal Transaction Count'],
        name=f'Illegal{suffix}',
        marker_color=illegal_color,
        legendgroup='group1',
        showlegend=True,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y}',
        textposition='auto',
        hovertext=counts['Illegal Transaction Count'].apply(lambda x: f'Illegal Transactions: {x:.2%}' if normalize_clicks % 2 == 1 else f'Illegal Transactions: {int(x)}'),
        hoverinfo='text'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=counts['Industry'],
        y=counts['Legal Transaction Count'],
        name=f'Legal{suffix}',
        marker_color=legal_color,
        legendgroup='group2',
        showlegend=True,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y}',
        textposition='auto',
        hovertext=counts['Legal Transaction Count'].apply(lambda x: f'Legal Transactions: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Transactions: {int(x)}'),
        hoverinfo='text'
    ), row=1, col=1)

    # Añadir traces para amounts (misma alineación: amounts['Industry'])
    fig.add_trace(go.Bar(
        x=amounts['Industry'],
        y=amounts['Illegal Amount (Millions USD)'],
        name=f'Illegal{suffix}',
        marker_color=illegal_color,
        legendgroup='group1',
        showlegend=False,  # no repetir leyenda en subplot 2
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y:.2f}',
        textposition='auto',
        hovertext=amounts['Illegal Amount (Millions USD)'].apply(lambda x: f'Illegal Amount: {x:.2%}' if normalize_clicks % 2 == 1 else f'Illegal Amount: {x:.2f}'),
        hoverinfo='text'
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=amounts['Industry'],
        y=amounts['Legal Amount (Millions USD)'],
        name=f'Legal{suffix}',
        marker_color=legal_color,
        legendgroup='group2',
        showlegend=False,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y:.2f}',
        textposition='auto',
        hovertext=amounts['Legal Amount (Millions USD)'].apply(lambda x: f'Legal Amount: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Amount: {x:.2f}'),
        hoverinfo='text'
    ), row=1, col=2)

    # Layout y estilos
    fig.update_layout(
        template='plotly_white',
        barmode='stack',
        legend=dict(
            title=dict(text="<b>Source of Money</b>", font=dict(size=18)),
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(0,0,0,0.08)",
            borderwidth=0,
            itemclick=False,
            itemdoubleclick=False,
            traceorder='normal'
        ),
        margin=dict(l=8, r=200, t=40, b=40),
        clickmode='none'
    )

    # Ejes
    fig.update_xaxes(title_text='Industry', row=1, col=1)
    fig.update_yaxes(title_text='Count', row=1, col=1)
    fig.update_xaxes(title_text='Industry', row=1, col=2)
    fig.update_yaxes(title_text='Amount (Millions USD)', row=1, col=2)

    return fig




# Line chart of transaction amount over time by country and stacked bar chart of total of transactions by industry. Each stack is a destination country

def make_transaction_over_time(dataset, iso_a3_dict, selected_industries, country_selected, window_size, selected_date):
    filtered_data = dataset[dataset['Industry'].isin(selected_industries) & (dataset['Country'].isin(country_selected))]
    transactions_over_time = filtered_data.groupby(['Country', 'Date'])['Amount (USD)'].sum().reset_index()

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2}, None], [{}, {}]],
        subplot_titles=(
            "Transaction Amount Over Time by Country",
            "Total Transactions with The Rest of The Countries"
        ),
        column_widths=[0.7, 0.3],
        row_heights=[1.5, 1.5]
    )

    # --- TRACKEAR países para construir la leyenda helper más tarde ---
    countries_seen = []

    # Fig 1: Transaction amount over time by country (líneas)
    for country in transactions_over_time['Country'].unique():
        country_data = transactions_over_time[transactions_over_time['Country'] == country].sort_values('Date')
        country_data['Amount (USD)'] = country_data['Amount (USD)'].rolling(window=window_size, min_periods=1).mean()

        iso_code = iso_a3_dict.get(country, '')
        color = country_color.get(iso_code, 'black')

        # Añadimos la traza de línea; NO mostramos leyenda aquí (la helper la hará)
        fig.add_trace(go.Scatter(
            x=country_data['Date'],
            y=country_data['Amount (USD)'],
            mode='lines+markers',
            name=country,
            legendgroup=country,
            line=dict(color=color),
            marker=dict(symbol='circle', size=6),
            hovertemplate=f"{country}<br>Date: %{{x}}<br>Total Amount: %{{y:.2f}} (USD)<extra></extra>",
            showlegend=False
        ), row=1, col=1)

        if country not in countries_seen:
            countries_seen.append(country)

    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Total Amount (USD)", row=1, col=1)

    # Fig 2: Total transactions by industry stacked by destination country (barras)
    industry_totals = filtered_data.groupby(['Country', 'Destination Country'])['Amount (USD)'].sum().reset_index()
    for des_country in industry_totals['Destination Country'].unique():
        des_country_data = industry_totals[industry_totals['Destination Country'] == des_country]
        iso_code = iso_a3_dict.get(des_country, '')
        color = country_color.get(iso_code, 'black')

        fig.add_trace(go.Bar(
            x=des_country_data['Country'],
            y=des_country_data['Amount (USD)'] / 1e6,  # Convert to millions
            name=des_country,
            legendgroup=des_country,
            marker=dict(color=color),
            hovertemplate=f"Destination: {des_country}<br>Total Amount: %{{y:.2f}} (Millions USD)<extra></extra>",
            showlegend=False
        ), row=2, col=1)

        if des_country not in countries_seen:
            countries_seen.append(des_country)

    fig.update_yaxes(title_text="Total Amount (Millions USD)", row=2, col=1)
    fig.update_xaxes(title_text="Origin Country", row=2, col=1)

    # Fig 3: Scatter plot (spend vs receive) - cada punto por país
    # Normalizamos la fecha para la comparación
    try:
        sel_date = pd.to_datetime(selected_date).date()
        # Asegurar que 'Date' es datetime; crear columna temporal de fecha si es necesario
        fd = filtered_data.copy()
        if np.issubdtype(fd['Date'].dtype, np.datetime64):
            fd['Date_only'] = fd['Date'].dt.date
            filtered_by_date = fd[fd['Date_only'] == sel_date]
        else:
            filtered_by_date = fd[fd['Date'] == selected_date]
    except Exception:
        # fallback si hay problemas con tipo de fecha
        filtered_by_date = filtered_data[filtered_data['Date'] == selected_date]

    send = filtered_by_date.groupby('Country')['Amount (USD)'].sum().reset_index(name='Spend Amount (USD)')
    receive = filtered_by_date.groupby('Destination Country')['Amount (USD)'].sum().reset_index(name='Receive Amount (USD)')

    scatter_data = pd.merge(send, receive, left_on='Country', right_on='Destination Country', how='outer').fillna(0)

    countries = filtered_data['Country'].unique().tolist() + filtered_data['Destination Country'].unique().tolist()
    countries = list(set(countries))

    # Repairs to ensure symmetry
    rows_origin = scatter_data[~scatter_data['Country'].isin(countries)]
    if not rows_origin.empty:
        rows_origin = rows_origin.copy()
        rows_origin['Spend Amount (USD)'] = 0
        rows_origin['Country'] = rows_origin['Destination Country']

    rows_destiny = scatter_data[~scatter_data['Destination Country'].isin(countries)]
    if not rows_destiny.empty:
        rows_destiny = rows_destiny.copy()
        rows_destiny['Receive Amount (USD)'] = 0
        rows_destiny['Destination Country'] = rows_destiny['Country']

    scatter_data = pd.concat([scatter_data, rows_origin, rows_destiny], ignore_index=True)
    scatter_data = scatter_data[(scatter_data['Country'].isin(countries)) & (scatter_data['Destination Country'].isin(countries))]

    scatter_size = 10 + (scatter_data['Spend Amount (USD)'] + scatter_data['Receive Amount (USD)']) / 1e6

    # Añadir scatter por país; no mostramos leyenda (la helper la añadirá)
    for country in scatter_data['Country'].unique():
        scatter_data_country = scatter_data[scatter_data['Country'] == country]
        iso_code = iso_a3_dict.get(country, '')
        color = country_name_color.get(country, country_color.get(iso_code, 'black'))

        fig.add_trace(go.Scatter(
            x=scatter_data_country['Spend Amount (USD)'] / 1e6,
            y=scatter_data_country['Receive Amount (USD)'] / 1e6,
            mode='markers+text',
            text=scatter_data_country['Country'],
            textfont=dict(size=10, color=color),
            marker=dict(size=scatter_size, color=color, opacity=0.7, symbol='circle'),
            hovertemplate=(
                "Country: %{text}<br>"
                "Spend Amount: %{x:.2f} (Millions USD)<br>"
                "Receive Amount: %{y:.2f} (Millions USD)<extra></extra>"
            ),
            name=country,
            legendgroup=country,
            showlegend=False,
        ), row=2, col=2)

        if country not in countries_seen:
            countries_seen.append(country)

    # Ejes y diagonal comparativa para el scatter
    max_amount = 0
    if not scatter_data.empty:
        max_amount = max(scatter_data['Spend Amount (USD)'].max(), scatter_data['Receive Amount (USD)'].max()) / 1e6
    else:
        max_amount = 0

    if max_amount > 0:
        fig.update_xaxes(range=[-max_amount * 0.25, max_amount * 1.25], row=2, col=2)
        fig.update_yaxes(range=[-max_amount * 0.25, max_amount * 1.25], row=2, col=2)
    else:
        fig.update_xaxes(row=2, col=2)
        fig.update_yaxes(row=2, col=2)

    fig.add_trace(go.Scatter(
        x=[-max_amount, max_amount],
        y=[-max_amount, max_amount],
        mode='lines',
        line=dict(color='LightGray', dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ), row=2, col=2)

    # --- Ahora añadimos las trazas "helper" de leyenda: una por país con icono CÍRCULO ---
    # Estas trazas aparecerán en la leyenda y, gracias a legendgroup, controlarían las trazas con el mismo legendgroup.
    for country in countries_seen:
        iso_code = iso_a3_dict.get(country, '')
        color = country_color.get(iso_code, 'black')
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(symbol='circle', size=12, color=color),
            name=country,
            legendgroup=country,
            showlegend=True
        ))

    # Layout final: leyenda pegada a la derecha exterior, NON-CLICKABLE, con título "COUNTRY LEGEND"
    fig.update_layout(
        height=800,
        title_text="",
        template='plotly_white',
        legend=dict(
            title=dict(text="<b>Country Legend</b>", font=dict(size=18)),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,           # posiciona la leyenda a la derecha exterior
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.06)",
            borderwidth=0,
            traceorder='normal',
            itemclick=False,           # <- deshabilita clic simple en items de la leyenda
            itemdoubleclick=False      # <- deshabilita doble clic
        ),
        margin=dict(l=8, r=260, t=40, b=40),  # aumentar r para que la leyenda no se corte
        clickmode='none'  # <- evita que clicks en la figura afecten trazas
    )

    # ---- Añadir títulos del scatter (ejes y subtítulo) ----
    # Títulos ejes X / Y para el scatter (fila 2, col 2)
    fig.update_xaxes(title_text=f"Spend Amount (Millions USD)", row=2, col=2)
    fig.update_yaxes(title_text=f"Receive Amount (Millions USD)", row=2, col=2)

    return fig
