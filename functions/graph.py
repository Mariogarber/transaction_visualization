import plotly.graph_objects as go
import random
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import folium
import io
import base64
import matplotlib
from dash import html
import dash_bootstrap_components as dbc
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def make_cards_for_industries(filtered_data):
    industry_counts = filtered_data.groupby('Industry')['Amount (USD)'].sum()
    industry_elements = list(industry_counts.items())
    industry_elements_ordered = sorted(industry_elements, key=lambda x: x[1])

    first_group = industry_elements[:len(industry_elements)//2]
    second_group = industry_elements[len(industry_elements)//2:]

    card_components = []

    for group in [first_group, second_group]:
        industry_items = []
        for industry, amount in group:
            color = color_map_industries.get(industry, '#6c757d')
            industry_items.extend([
                html.H3(
                    industry, 
                    className="card-title", 
                    style={
                        'color': color_map_industries.get(industry, '#6c757d'), 
                        'margin': '10px 0',
                        'fontWeight': 'bold',
                        'fontSize': f'{1.2 + 0.1*industry_elements_ordered.index((industry, amount))}rem',
                        'letterSpacing': '0.5px',
                        'textShadow': '1px 1px 0px black, -1px -1px 0px black, 1px -1px 0px black, -1px 1px 0px black'
                        }
                    ),
                html.H2(
                    f"${amount/1_000_000:,.2f}M", 
                    className="card-text", 
                    style={
                        'color': color, 
                        'margin': '0 0 20px 0',
                        'fontWeight': '700',
                        'fontSize': f'{1.4 + 0.2*industry_elements_ordered.index((industry, amount))}rem',
                        'textShadow': '1px 1px 0px black, -1px -1px 0px black, 1px -1px 0px black, -1px 1px 0px black'
                        }
                    )
                ])
        
        card = dbc.Card([
                dbc.CardBody(industry_items,
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
                'minWidth': '400px',
                'minHeight': '200px',
                'background': 'linear-gradient(135deg, #eeeeee 0%, #aaaaaa 100%)',
                'border': '2px solid #6c757d',
                'transition': 'all 0.3s ease-in-out',
                'cursor': 'pointer',
                'position': 'relative',
                'overflow': 'hidden'
            },
        className="h-100 shadow-lg"
        )

        card_components.append(card)

    return card_components

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
    # Color each country based on the total amount received
    amount_colors = {}
    for iso, amt in total.items():
        amount_colors[iso] = get_color(amt, min_amt, max_amt)

    # Add choropleth layer for countries
    fig.add_trace(go.Choropleth(
        locations=list(amount_colors.keys()),
        z=list(total.values),
        text=[admin for admin in gdf_countries.set_index('iso_a3').loc[list(amount_colors.keys()), 'admin']],
        colorscale=[c[1] for c in colorscale],
        autocolorscale=True,
        marker_line_color='white',
        colorbar_title="Flow Amount (USD)",
        hoverinfo='text',
        hovertemplate='%{text}<br>Flow Amount: %{z:.2f} (USD)<extra></extra>',
        geo='geo',
        showscale=True
    ))

    # Add arrows for flows
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
                line=dict(width=[0, 0], color=['blue', country_color.get(r['origin_iso_a3'], 'black')])
            ),
            opacity=0.7,
            hoverinfo='text',
            text=[
            f"Origen: {r['origin_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['origin_iso_a3'], 'admin']})<br>"
            f"Destino: {r['dest_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['dest_iso_a3'], 'admin']})<br>"
            f"Flujo: -{r['amount']/1e6:03f} Millions (USD)",
            f"Origen: {r['origin_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['origin_iso_a3'], 'admin']})<br>"
            f"Destino: {r['dest_iso_a3']} ({gdf_countries.set_index('iso_a3').loc[r['dest_iso_a3'], 'admin']})<br>"
            f"Flujo: +{r['amount']/1e6:03f} Millions (USD)"
            ],
            showlegend=False
        ))

    if show_arrows:
        for trace in traces:
            fig.add_trace(trace)

    # Add legend for countries colors
    legend_traces = []
    for iso, color in country_color.items():
        admin_name = gdf_countries.set_index('iso_a3').loc[iso, 'admin'] if iso in gdf_countries['iso_a3'].values else iso
        legend_traces.append(go.Scattergeo(
            lon=[None], lat=[None],  # invisible points
            mode='markers',
            marker=dict(size=12, color=color),
            name=admin_name,
            text=f"Send by {admin_name}",
            showlegend=True
        ))

    if show_arrows:
        for trace in legend_traces:
            fig.add_trace(trace)

    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.7)"
        )
    )

    # Update geo layout to color countries and set projection
    fig.update_geos(
        projection_type='natural earth',
        showcountries=True,
        showcoastlines=True,
        showland=True,
        showocean=True,
        showlakes=True,
        oceancolor="#2391FF",
        lakecolor="#82C0FF",
        landcolor="#C2A580",
        coastlinecolor="#A0A0A0",
        resolution=110
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode='closest',
        title=f"Transacciones del {selected_date}"
    )
    return fig, flows

# Stacked Bar Charts with legal vs illegal transactions by industry and country

def make_stacked_illegal_legal(selected_country, normalize_clicks, dataset):
    filtered_data = dataset[dataset['Country'] == selected_country]
    filtered_data['Amount (USD)'] = filtered_data['Amount (USD)'] / 1e6
    illegal_data = filtered_data[filtered_data['Source of Money'] == 'Illegal']
    legal_data = filtered_data[filtered_data['Source of Money'] == 'Legal']

    # Agrupa por industria
    industry_group_illegal = illegal_data.groupby('Industry')
    industry_group_legal = legal_data.groupby('Industry')
    
    #illegal data
    illegal_counts = industry_group_illegal.size().reset_index(name='Illegal Transaction Count')
    illegal_amounts = industry_group_illegal['Amount (USD)'].sum().reset_index(name='Illegal Amount (USD)')
    illegal_amounts['Illegal Amount (Millions USD)'] = illegal_amounts['Illegal Amount (USD)']

    # legal_data
    legal_counts = industry_group_legal.size().reset_index(name='Legal Transaction Count')
    legal_amounts = industry_group_legal['Amount (USD)'].sum().reset_index(name='Legal Amount (USD)')
    legal_amounts['Legal Amount (Millions USD)'] = legal_amounts['Legal Amount (USD)']

    # Subplots: bar chart (count) + bar chart (amount)
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['Transaction Count', 'Amount (Millions USD)'],
        shared_yaxes=False
    )

    suffix = ""
    if normalize_clicks % 2 == 1:
        suffix = " (Normalized)"

        # Normalize counts
        total_counts = illegal_counts['Illegal Transaction Count'] + legal_counts['Legal Transaction Count']
        illegal_counts['Illegal Transaction Count'] = illegal_counts['Illegal Transaction Count'] / total_counts
        legal_counts['Legal Transaction Count'] = legal_counts['Legal Transaction Count'] / total_counts

        # Normalize amounts
        total_amounts = illegal_amounts['Illegal Amount (USD)'] + legal_amounts['Legal Amount (USD)']
        # Avoid division by zero and align indices
        total_amounts = total_amounts.replace(0, np.nan)
        illegal_amounts['Illegal Amount (Millions USD)'] = illegal_amounts['Illegal Amount (USD)'] / total_amounts
        legal_amounts['Legal Amount (Millions USD)'] = legal_amounts['Legal Amount (USD)'] / total_amounts

    # Add traces for count subplot
    fig.add_trace(go.Bar(
        x=illegal_counts['Industry'],
        y=illegal_counts['Illegal Transaction Count'],
        name=f'Illegal{suffix}',
        marker_color="#FF4747",
        legendgroup='group1',
        showlegend=True,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y}',
        textposition='auto',
        hovertext=illegal_counts['Illegal Transaction Count'].apply(lambda x: f'Illegal Transactions: {x:.2%}' if normalize_clicks % 2 == 1 else f'Illegal Transactions: {x}'),
        hoverinfo='text'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=legal_counts['Industry'],
        y=legal_counts['Legal Transaction Count'],
        name=f'Legal{suffix}',
        marker_color='#77DD77',
        legendgroup='group2',
        showlegend=True,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y}',
        textposition='auto',
        hovertext=legal_counts['Legal Transaction Count'].apply(lambda x: f'Legal Transactions: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Transactions: {x}'),
        hoverinfo='text'
    ), row=1, col=1)

    # Add traces for amount subplot, but don't show legend again
    fig.add_trace(go.Bar(
        x=illegal_amounts['Industry'],
        y=illegal_amounts['Illegal Amount (Millions USD)'],
        name=f'Illegal{suffix}',
        marker_color="#FF4747",
        legendgroup='group1',
        showlegend=False,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y:.2f}',
        textposition='auto',
        hovertext=illegal_amounts['Illegal Amount (Millions USD)'].apply(lambda x: f'Illegal Amount: {x:.2%}' if normalize_clicks % 2 == 1 else f'Illegal Amount: {x:.2f}'),
        hoverinfo='text'
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=legal_amounts['Industry'],
        y=legal_amounts['Legal Amount (Millions USD)'],
        name=f'Legal{suffix}',
        marker_color='#77DD77',
        legendgroup='group2',
        showlegend=False,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y:.2f}',
        textposition='auto',
        hovertext=legal_amounts['Legal Amount (Millions USD)'].apply(lambda x: f'Legal Amount: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Amount: {x:.2f}'),
        hoverinfo='text'
    ), row=1, col=2)

    fig.update_layout(
        title='Transaction Overview by Industry',
        template='plotly_white',
        legend_title_text='Source of Money',
        barmode='stack'
    )

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
            "Total Transactions by Industry and Destination Country"
        ),
        column_widths=[0.7, 0.3],
        row_heights=[1.5, 1.5]
    )

    # Fig 1: Transaction amount over time by country
    for country in transactions_over_time['Country'].unique():
        country_data = transactions_over_time[transactions_over_time['Country'] == country]
        # Add a windowed average to smooth the line
        country_data = country_data.sort_values('Date')
        country_data['Amount (USD)'] = country_data['Amount (USD)'].rolling(window=window_size, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=country_data['Date'],
            y=country_data['Amount (USD)'],
            mode='lines+markers',
            name=country,
            line=dict(color=country_color.get(iso_a3_dict.get(country, ''), 'black')),
            hovertemplate=f"{country}<br>Date: %{{x}}<br>Total Amount: %{{y:.2f}} (USD)<extra></extra>",
            showlegend=True
        ), row=1, col=1)

    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Total Amount (USD)", row=1, col=1)
    fig.update_layout(title="Transaction Amount Over Time by Country")
    fig.update_layout(barmode='stack', title="Total Transactions by Industry and Destination Country")

    # Fig 2: Total of transactions by industry. Stack bar plot, each stack is a destination country
    industry_totals = filtered_data.groupby(['Country', 'Destination Country'])['Amount (USD)'].sum().reset_index()
    for des_country in industry_totals['Destination Country'].unique():
        des_country_data = industry_totals[industry_totals['Destination Country'] == des_country]
        fig.add_trace(go.Bar(
            x=des_country_data['Country'],
            y=des_country_data['Amount (USD)'] / 1e6,  # Convert to millions
            name=des_country,
            marker=dict(color=country_color.get(iso_a3_dict.get(des_country, ''), 'black')),
            hovertemplate=f"Destination: {des_country}<br>Total Amount: %{{y:.2f}} (Millions USD)<extra></extra>",
            legendgroup=f"countries_{des_country}"
        ), row=2, col=1)

    fig.update_yaxes(title_text="Total Amount (Millions USD)", row=2, col=1)
    fig.update_xaxes(title_text="Origin Country", row=2, col=1)
    fig.update_layout(barmode='stack')

    # Fig 3: Scatter plot where x is spend transactions and y is received transactions
    filtered_by_date = filtered_data[filtered_data['Date'] == selected_date]
    send = filtered_by_date.groupby('Country')['Amount (USD)'].sum().reset_index(name='Spend Amount (USD)')
    receive = filtered_by_date.groupby('Destination Country')['Amount (USD)'].sum().reset_index(name='Receive Amount (USD)')

    scatter_data = pd.merge(send, receive, left_on='Country', right_on='Destination Country', how='outer').fillna(0)

    countries = filtered_data['Country'].unique().tolist() + filtered_data['Destination Country'].unique().tolist()
    countries = list(set(countries))  # Remove duplicates

    # Get the rows where country is not in countries list
    rows_origin = scatter_data[~scatter_data['Country'].isin(countries)]
    rows_origin['Spend Amount (USD)'] = 0
    rows_origin['Country'] = rows_origin['Destination Country']

    rows_destiny = scatter_data[~scatter_data['Destination Country'].isin(countries)]
    rows_destiny['Receive Amount (USD)'] = 0
    rows_destiny['Destination Country'] = rows_destiny['Country']

    scatter_data = pd.concat([scatter_data, rows_origin, rows_destiny], ignore_index=True)

    # Drops the rows where Country or Destination Country is not in countries list
    scatter_data = scatter_data[(scatter_data['Country'].isin(countries)) & (scatter_data['Destination Country'].isin(countries))]

    scatter_size = 10 + (scatter_data['Spend Amount (USD)'] + scatter_data['Receive Amount (USD)']) / 1e6  # Size based on total amount in millions

    for country in scatter_data['Country'].unique():
        scatter_data_country = scatter_data[scatter_data['Country'] == country]
        fig.add_trace(go.Scatter(
            x=scatter_data_country['Spend Amount (USD)'] / 1e6,  # Convert to millions
            y=scatter_data_country['Receive Amount (USD)'] / 1e6,  # Convert to millions
            mode='markers+text',
            text=scatter_data_country['Country'],
            textfont=dict(size=1, color=country_name_color.get(country, 'black')),
            marker=dict(size=scatter_size, color=scatter_data_country['Country'].map(country_name_color), opacity=0.7),
            hovertemplate=(
            "Country: %{text}<br>"
            "Spend Amount: %{x:.2f} (Millions USD)<br>"
            "Receive Amount: %{y:.2f} (Millions USD)<extra></extra>"
            ),
            showlegend=False,
            name='Spend vs Receive',
            legendgroup=f"countries_{country}"
        ), row=2, col=2)

    # Set the xticks and yticks to be the same for better comparison
    max_amount = max(scatter_data['Spend Amount (USD)'].max(), scatter_data['Receive Amount (USD)'].max()) / 1e6
    fig.update_xaxes(range=[-max_amount * 0.25, max_amount * 1.25], row=2, col=2)
    fig.update_yaxes(range=[-max_amount * 0.25, max_amount * 1.25], row=2, col=2)

    fig.update_xaxes(title_text=f"Spend Amount (Millions USD) on {selected_date}", row=2, col=2)
    fig.update_yaxes(title_text=f"Receive Amount (Millions USD) on {selected_date}", row=2, col=2)
    # add a diagonal line
    fig.add_trace(go.Scatter(
        x=[-max_amount, max_amount],
        y=[-max_amount, max_amount],
        mode='lines',
        line=dict(color='LightGray', dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ), row=2, col=2)

    fig.update_layout(height=800, title_text="Transaction Analysis")

    return fig
