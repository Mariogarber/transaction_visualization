"""
Geographical visualization functions.
"""
import plotly.graph_objects as go
import random
import pandas as pd
import numpy as np
import folium
import io
import base64
from folium.plugins import Fullscreen
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Color mappings
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


def make_info_folium_map(clean_data_illegal, geo_data, map_illegal_data, map_transactions_data):
    """Create an interactive Folium map with transaction information"""
    # Create map with better tiles and controls
    map = folium.Map(
        location=[20, 0], 
        zoom_start=2,
        tiles=None  # We'll add custom tiles
    )
    
    # Add multiple tile layers for better visualization
    folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(map)
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(map)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(map)
    
    # Add fullscreen button
    Fullscreen().add_to(map)

    # Enhanced Choropleth layer for total illegal amount by country
    folium.Choropleth(
        geo_data=geo_data[['admin', 'geometry']],
        name='Total Illegal Amount (Background)',
        data=clean_data_illegal.groupby('Country')['Amount (USD)'].sum() / 1e6,
        columns=['admin', 'Illegal Ratio'],
        key_on='feature.properties.admin',
        fill_color='YlOrRd',
        fill_opacity=0.6,
        line_opacity=0.3,
        line_color='white',
        line_weight=1,
        legend_name='Total Illegal Amount (Millions USD)',
        smooth_factor=0.5
    ).add_to(map)

    # Combined layer with both pie charts and bar charts in popups
    fg_markers = folium.FeatureGroup(name="📊📈 Country Analysis (Combined Charts)")
    
    for country, ratio in map_illegal_data.items():
        geometry = geo_data[geo_data['admin'] == country].geometry
        if geometry.empty:
            continue
        centroid = geometry.values[0].centroid
        
        # Create mini pie chart and bar chart
        data = map_transactions_data.get(country, {})
        
        # Create the popup content with charts
        popup_html = create_country_popup(country, ratio, data, clean_data_illegal)
        
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=folium.Popup(popup_html, max_width=450),
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 12px; color: red;">
                    <i class="fa fa-chart-pie" aria-hidden="true"></i>
                </div>""")
        ).add_to(fg_markers)
    
    fg_markers.add_to(map)
    
    # Add layer control
    folium.LayerControl().add_to(map)
    
    # Convert map to HTML string
    map_html = map._repr_html_()
    
    # Return the HTML directly for srcDoc (no base64 encoding needed)
    return map_html


def make_transaction_arrow_map(flows, gdf_countries, selected_date, total, min_amt, max_amt, show_arrows):
    """Create transaction flow map with arrows between countries"""
    fig = go.Figure()

    # --- Normalize 'total' to a dict iso -> numeric_value ---
    total_map = {}
    try:
        for k, v in (total.items() if hasattr(total, 'items') else enumerate(total)):
            total_map[k] = v
    except Exception:
        try:
            if hasattr(total, 'index'):
                for k in total.index:
                    total_map[k] = total[k]
        except Exception:
            total_map = {}

    # If total was a list/array without ISO keys, try to map by order
    if not total_map and isinstance(total, (list, tuple, np.ndarray)):
        try:
            isos = list(gdf_countries['iso_a3'].values)
            for i, val in enumerate(total):
                if i < len(isos):
                    total_map[isos[i]] = val
        except Exception:
            total_map = {}

    # --- Prepare arrays for choropleth ---
    locations = []
    z_values = []
    text_admins = []
    for iso, amt in total_map.items():
        locations.append(iso)
        try:
            z_values.append(float(amt))
        except Exception:
            z_values.append(0.0)
        if iso in gdf_countries['iso_a3'].values:
            text_admins.append(gdf_countries.set_index('iso_a3').loc[iso, 'admin'])
        else:
            text_admins.append(iso)

    # Add choropleth if we have numeric data
    if locations and any([v is not None for v in z_values]):
        decimals = 1
        z_values_m = [float(v) / 1e6 for v in z_values]
        zmin_m = (min_amt / 1e6) if (min_amt is not None) else None
        zmax_m = (max_amt / 1e6) if (max_amt is not None) else None

        fig.add_trace(go.Choropleth(
            locations=locations,
            z=z_values_m,
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
                tickformat=f",.{decimals}f"
            ),
            hoverinfo='text',
            hovertemplate=f'%{{text}}<br>Flow Amount: %{{z:,.{decimals}f}} Millions (USD)<extra></extra>',
            geo='geo',
            showscale=True,
            showlegend=False
        ))

        fig.update_layout(
            margin=dict(l=0, r=170, t=30, b=0),
            clickmode='none'
        )

    # --- Add arrows for flows ---
    traces = []
    
    # Calculate normalization for arrow scaling
    if len(flows) > 0:
        flow_amounts = flows['amount']
        min_flow = flow_amounts.min()
        max_flow = flow_amounts.max()
        flow_range = max_flow - min_flow if max_flow > min_flow else 1
        
        def normalize_line_width(amount):
            normalized = (amount - min_flow) / flow_range
            return 1 + normalized * 7
            
        def normalize_marker_size(amount):
            normalized = (amount - min_flow) / flow_range
            return 4 + normalized * 16
    else:
        def normalize_line_width(amount):
            return 2
        def normalize_marker_size(amount):
            return 8
    
    for _, r in flows.iterrows():
        origin_iso = r['origin_iso_a3']
        origin_name = gdf_countries.set_index('iso_a3').loc[origin_iso, 'admin'] if origin_iso in gdf_countries['iso_a3'].values else origin_iso
        
        traces.append(go.Scattergeo(
            lon=[r['o_lon'], r['d_lon'] + random.uniform(-1.5, 1.5)],
            lat=[r['o_lat'], r['d_lat'] + random.uniform(-1.5, 1.5)],
            mode='lines+markers',
            line=dict(width=normalize_line_width(r['amount']), color=country_color.get(r['origin_iso_a3'], 'black')),
            marker=dict(
                size=[0, normalize_marker_size(r['amount'])],
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
            name=origin_name,
            legendgroup=origin_name,
            showlegend=False
        ))

    if show_arrows:
        for trace in traces:
            fig.add_trace(trace)

    # --- Dynamic legend for ISOs present in flows ---
    isos_present = set()
    possible_iso_cols = ['origin_iso_a3', 'origin', 'o_iso', 'o_iso_a3', 'dest_iso_a3', 'dest', 'd_iso', 'd_iso_a3']
    for col in possible_iso_cols:
        if col in flows.columns:
            isos_present.update([v for v in flows[col].dropna().unique()])

    legend_traces = []
    for iso in sorted(isos_present):
        if not iso:
            continue
        try:
            admin_name = gdf_countries.set_index('iso_a3').loc[iso, 'admin'] if (('iso_a3' in gdf_countries.columns) and (iso in gdf_countries['iso_a3'].values)) else iso
        except Exception:
            admin_name = iso

        color = country_color.get(iso, None) or country_name_color.get(admin_name, None) or 'black'

        legend_traces.append(go.Scattergeo(
            lon=[None], lat=[None],
            mode='markers',
            marker=dict(size=12, color=color),
            name=admin_name,
            legendgroup=admin_name,
            text=f"Send by {admin_name}",
            showlegend=True
        ))

    if show_arrows:
        for trace in legend_traces:
            fig.add_trace(trace)

    # --- Interactive legend for controlling arrow visibility ---
    fig.update_layout(
        legend=dict(
            title=dict(text="<b>Arrow legend (Click to Hide/Show)</b>", font=dict(size=15, color="#000000")),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.85)",
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            traceorder='normal'
        )
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


def make_risk_score_choropleth_map(dataset):
    """Create a choropleth map showing average money laundering risk scores by country."""
    # Calculate average risk score by country
    country_risk = dataset.groupby('Country').agg({
        'Money Laundering Risk Score': ['mean', 'count'],
        'Amount (USD)': 'sum'
    }).round(2)
    
    country_risk.columns = ['Avg_Risk_Score', 'Transaction_Count', 'Total_Amount']
    country_risk = country_risk.reset_index()
    
    # Create country code mapping for choropleth
    country_code_map = {
        'USA': 'USA',
        'South Africa': 'ZAF', 
        'Switzerland': 'CHE',
        'Russia': 'RUS',
        'Brazil': 'BRA',
        'UK': 'GBR',
        'India': 'IND',
        'China': 'CHN',
        'Singapore': 'SGP',
        'UAE': 'ARE'
    }
    
    country_risk['Country_Code'] = country_risk['Country'].map(country_code_map)
    
    # Create choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=country_risk['Country_Code'],
        z=country_risk['Avg_Risk_Score'],
        locationmode='ISO-3',
        colorscale='Reds',
        autocolorscale=False,
        text=country_risk['Country'],
        hovertemplate=
        '<b>%{text}</b><br>'+
        'Average Risk Score: %{z:.2f}<br>'+
        'Total Transactions: %{customdata[0]:,}<br>'+
        'Total Amount: $%{customdata[1]:,.0f}<br>'+
        '<extra></extra>',
        customdata=country_risk[['Transaction_Count', 'Total_Amount']].values,
        colorbar=dict(
            title="Average<br>Risk Score",
            titleside="top",
            tickmode="linear",
            tick0=1,
            dtick=1,
            thickness=15,
            len=0.8
        )
    ))
    
    fig.update_layout(
        title={
            'text': 'Money Laundering Risk Score by Country',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            lakecolor='rgba(0,0,0,0)',
            landcolor='#f8f9fa',
            coastlinecolor='#bdc3c7'
        ),
        height=500,
        margin=dict(t=60, b=20, l=20, r=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_country_popup(country, ratio, data, clean_data_illegal):
    """Helper function to create popup content for country markers"""
    try:
        # Get country-specific data to calculate totals
        country_data = clean_data_illegal[clean_data_illegal['Country'] == country]
        
        if not country_data.empty:
            total_count = len(country_data)
            total_amount = country_data['Amount (USD)'].sum()
            count_str = f"{total_count:,}"
            amount_str = f"${total_amount:,.0f}"
            
            # Create transaction type breakdown
            transaction_breakdown = ""
            if data:  # data contains transaction type counts
                transaction_breakdown = "<h5>Transaction Types:</h5><ul>"
                for trans_type, count in data.items():
                    percentage = (count / total_count) * 100 if total_count > 0 else 0
                    transaction_breakdown += f"<li>{trans_type}: {count} ({percentage:.1f}%)</li>"
                transaction_breakdown += "</ul>"
            
            # Create a simple pie chart using matplotlib
            chart_html = ""
            if data and len(data) > 0:
                try:
                    import matplotlib.pyplot as plt
                    import io
                    import base64
                    
                    # Create pie chart
                    fig, ax = plt.subplots(figsize=(4, 3))
                    labels = list(data.keys())
                    sizes = list(data.values())
                    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                    
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                    ax.set_title('Transaction Types Distribution')
                    
                    # Convert plot to base64 string
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=80)
                    buffer.seek(0)
                    plot_data = buffer.getvalue()
                    buffer.close()
                    plt.close(fig)
                    
                    # Encode plot
                    plot_url = base64.b64encode(plot_data).decode()
                    chart_html = f'<img src="data:image/png;base64,{plot_url}" style="width: 100%; max-width: 280px;"/>'
                
                except Exception as e:
                    chart_html = f"<p style='color: red;'>Chart error: {str(e)}</p>"
        else:
            count_str = "N/A"
            amount_str = "$N/A"
            transaction_breakdown = ""
            chart_html = ""
            
    except Exception as e:
        count_str = "N/A"
        amount_str = "$N/A"
        transaction_breakdown = f"<p style='color: red;'>Data error: {str(e)}</p>"
        chart_html = ""
    
    return f"""
    <div style="width: 350px;">
        <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{country}</h4>
        <p><strong>Illegal Transaction Ratio:</strong> {ratio:.2%}</p>
        <p><strong>Total Transactions:</strong> {count_str}</p>
        <p><strong>Total Amount:</strong> {amount_str}</p>
        {transaction_breakdown}
        {chart_html}
    </div>
    """