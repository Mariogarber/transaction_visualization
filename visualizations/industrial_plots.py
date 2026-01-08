"""
Industrial analysis visualization functions.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta


# Color mappings
color_map_industries = {
    'Arms Trade': "#ed5903",
    'Construction': "#2eaf4d",
    'Luxury Goods': '#ffc107',
    'Casinos': '#17a2b8',
    'Oil & Gas': "#8550e8",
    'Real Estate': "#f23f92",
    'Finance': "#c5e03eb3",
}

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


def _normalize_color_for_plotly(color):
    """
    Accepts: '#RRGGBBAA', '#RRGGBB', '#RGB', 'rgb(...)', 'rgba(...)', CSS names.
    Returns: color in format accepted by Plotly: '#RRGGBB' or 'rgba(r,g,b,a)' or original string.
    """
    if color is None:
        return None
    if not isinstance(color, str):
        return color

    c = color.strip()
    # #RRGGBBAA -> rgba(...)
    if c.startswith('#') and len(c) == 9:  # including '#'
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            a = int(c[7:9], 16) / 255.0
            return f'rgba({r},{g},{b},{a:.3f})'
        except Exception:
            return c  # fallback, return as is
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

# --- SARIMA predictor plot ---
def make_sarima_predictor_figure(dataset, selected_country, selected_industries, train_start, train_end, forecast_periods=12):
    """
    Create a SARIMA prediction plot for spend money time series.
    Filters by country, industries, and date range for training.
    """
    # Filter data
    df = dataset.copy()
    df = df[(df['Country'] == selected_country) & (df['Industry'].isin(selected_industries))]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    # Filter by train period
    mask = (df['Date'] >= pd.to_datetime(train_start)) & (df['Date'] <= pd.to_datetime(train_end))
    train_df = df.loc[mask]
    # Aggregate by date
    ts = train_df.groupby('Date')['Amount (USD)'].sum().asfreq('D').fillna(0)
    # If not enough data, return empty fig
    if len(ts) < 10:
        return go.Figure(layout={"title": "Not enough data for SARIMA prediction."})
    # Fit SARIMA (simple order, can be improved)
    try:
        model = SARIMAX(ts, order=(1,1,1), seasonal_order=(1,1,1,7), enforce_stationarity=False, enforce_invertibility=False)
        results = model.fit(disp=False)
        forecast = results.get_forecast(steps=forecast_periods)
        pred_ci = forecast.conf_int()
        forecast_index = pd.date_range(ts.index[-1] + timedelta(days=1), periods=forecast_periods, freq='D')
        forecast_values = forecast.predicted_mean.values.clip(min=0)
        forecast_series = pd.Series(forecast_values, index=forecast_index)
        # Clip confidence interval to 0
        pred_ci_clipped = pred_ci.clip(lower=0)
    except Exception as e:
        return go.Figure(layout={"title": f"SARIMA error: {e}"})
    # Connect train to forecast by appending first forecast point to train
    train_x = list(ts.index) + [forecast_series.index[0]]
    train_y = list(ts.values) + [forecast_series.values[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_x, y=train_y, mode='lines+markers', name='Train Data'))
    fig.add_trace(go.Scatter(x=forecast_series.index, y=forecast_series.values, mode='lines+markers', name='Forecast'))
    # Add confidence interval (clipped)
    fig.add_traces([
        go.Scatter(
            x=forecast_index,
            y=pred_ci_clipped.iloc[:, 0],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            x=forecast_index,
            y=pred_ci_clipped.iloc[:, 1],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(width=0),
            showlegend=True,
            name='Confidence Interval'
        )
    ])
    fig.update_layout(
        title=f'SARIMA Spend Prediction ({selected_country}, {", ".join(selected_industries)})',
        xaxis_title='Date',
        yaxis_title='Amount (USD)',
        template='plotly_white',
        height=500
    )
    return fig


def make_industry_bar_figure(dataset, visible_industries=None, palette='Plotly', height_per_item=48, min_height=420):
    """Create industry bar chart with optional filtering"""
    industry_sums = (dataset.groupby('Industry', as_index=False)['Amount (USD)']
                    .sum()
                    .rename(columns={'Amount (USD)': 'Amount_USD'}))

    # Filter by visible industries if provided
    if visible_industries:
        industry_sums = industry_sums[industry_sums['Industry'].isin(visible_industries)]

    industry_elements = list(industry_sums.set_index('Industry')['Amount_USD'].items())
    industry_elements_ordered = sorted(industry_elements, key=lambda x: x[1])
    ordered_industries = [ind for ind, amt in industry_elements_ordered]
    industry_sums = industry_sums.set_index('Industry').reindex(ordered_industries).reset_index()

    industry_sums['Amount_M'] = industry_sums['Amount_USD'] / 1_000_000
    n = len(industry_sums)
    if n == 0:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available for selected industries",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return empty_fig

    # Dynamic height
    height = max(min_height, 48 * n + 120)

    color_map_processed = {k: _normalize_color_for_plotly(v) for k, v in color_map_industries.items()}

    # Create bar chart
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

    # Text on bars
    fig.update_traces(texttemplate='$%{y:,.0f}M', textposition='outside', cliponaxis=False)

    # Calculate y-range dynamically
    try:
        y_min = float(industry_sums['Amount_M'].min())
        y_max = float(industry_sums['Amount_M'].max())
    except Exception:
        y_min = None
        y_max = None

    if y_min is not None and y_max is not None and not (np.isnan(y_min) or np.isnan(y_max)):
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
    else:
        y_range = None

    # Layout
    yaxis_dict = dict(title='Amount (USD) — Millions', tickformat=',.0f')
    if y_range is not None:
        yaxis_dict['range'] = y_range

    fig.update_layout(
        autosize=True,
        height=height,
        margin=dict(l=80, r=80, t=60, b=60),
        xaxis=dict(title='', tickangle=0, tickfont=dict(size=18), automargin=True),
        yaxis=yaxis_dict,
        template='plotly_white',
        bargap=0.15,
        bargroupgap=0.02,
        showlegend=False
    )

    # Update font sizes
    fig.update_xaxes(tickfont=dict(size=18, family="Arial"))
    fig.update_yaxes(tickfont=dict(size=16, family="Arial"))
    fig.update_traces(textfont=dict(size=16))

    return fig

def make_stacked_illegal_legal(selected_country, normalize_clicks, dataset):
    """Create stacked bar chart of legal vs illegal transactions by industry"""
    # Filter and convert to millions
    filtered = dataset[dataset['Country'] == selected_country].copy()
    if filtered.empty:
        # Empty figure if no data
        fig_empty = make_subplots(rows=1, cols=2, subplot_titles=['Transaction Count', 'Amount (Millions USD)'])
        fig_empty.update_layout(template='plotly_white')
        return fig_empty

    filtered['Amount (USD)'] = filtered['Amount (USD)'] / 1e6

    # Group by Industry and Source of Money
    counts = (filtered
              .groupby(['Industry', 'Source of Money'])
              .size()
              .unstack(fill_value=0))

    amounts = (filtered
               .groupby(['Industry', 'Source of Money'])['Amount (USD)']
               .sum()
               .unstack(fill_value=0))

    # Ensure columns exist
    for col in ['Illegal', 'Legal']:
        if col not in counts.columns:
            counts[col] = 0
        if col not in amounts.columns:
            amounts[col] = 0

    # Consistent ordering by industry
    counts = counts.reset_index().sort_values('Industry')
    amounts = amounts.reset_index().sort_values('Industry')

    # Rename for clarity
    counts = counts.rename(columns={'Illegal': 'Illegal Transaction Count', 'Legal': 'Legal Transaction Count'})
    amounts = amounts.rename(columns={'Illegal': 'Illegal Amount (Millions USD)', 'Legal': 'Legal Amount (Millions USD)'})

    # Optional normalization
    suffix = ""
    if normalize_clicks % 2 == 1:
        suffix = " (Normalized)"
        # Counts normalization
        total_counts = counts['Illegal Transaction Count'] + counts['Legal Transaction Count']
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

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['Transaction Count', 'Amount (Millions USD)'],
        shared_yaxes=False
    )

    # Colors
    illegal_color = "#FF4747"
    legal_color = "#77DD77"

    # Add traces for counts
    fig.add_trace(go.Bar(
        x=counts['Industry'],
        y=counts['Illegal Transaction Count'],
        name=f'Illegal{suffix}',
        marker_color=illegal_color,
        legendgroup='illegal',
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
        legendgroup='legal',
        showlegend=True,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y}',
        textposition='auto',
        hovertext=counts['Legal Transaction Count'].apply(lambda x: f'Legal Transactions: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Transactions: {int(x)}'),
        hoverinfo='text'
    ), row=1, col=1)

    # Add traces for amounts
    fig.add_trace(go.Bar(
        x=amounts['Industry'],
        y=amounts['Illegal Amount (Millions USD)'],
        name=f'Illegal{suffix}',
        marker_color=illegal_color,
        legendgroup='illegal',
        showlegend=False,  # Don't repeat legend
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
        legendgroup='legal',
        showlegend=False,
        texttemplate='%{y:.2%}' if normalize_clicks % 2 == 1 else '%{y:.2f}',
        textposition='auto',
        hovertext=amounts['Legal Amount (Millions USD)'].apply(lambda x: f'Legal Amount: {x:.2%}' if normalize_clicks % 2 == 1 else f'Legal Amount: {x:.2f}'),
        hoverinfo='text'
    ), row=1, col=2)

    # Layout and styling
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
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            traceorder='normal'
        ),
        margin=dict(l=8, r=200, t=40, b=40)
    )

    # Axes
    fig.update_xaxes(title_text='Industry', row=1, col=1)
    fig.update_yaxes(title_text='Count', row=1, col=1)
    fig.update_xaxes(title_text='Industry', row=1, col=2)
    fig.update_yaxes(title_text='Amount (Millions USD)', row=1, col=2)

    return fig

def make_transaction_over_time(dataset, iso_a3_dict, selected_industries, country_selected, window_size):
    """Create transaction over time analysis with multiple visualizations"""
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

    # Track countries for legend
    countries_seen = []

    # Fig 1: Transaction amount over time by selected origin countries (lines)
    transactions_by_origin = filtered_data.groupby(['Country', 'Date'])['Amount (USD)'].sum().reset_index()
    
    for origin_country in country_selected:
        if origin_country in transactions_by_origin['Country'].unique():
            country_data = transactions_by_origin[transactions_by_origin['Country'] == origin_country].sort_values('Date')
            country_data['Amount (USD)'] = country_data['Amount (USD)'].rolling(window=window_size, min_periods=1).mean()

            iso_code = iso_a3_dict.get(origin_country, '')
            color = country_color.get(iso_code, 'black')

            # Add line chart trace
            fig.add_trace(go.Scatter(
                x=country_data['Date'],
                y=country_data['Amount (USD)'],
                mode='lines+markers',
                name=origin_country,
                legendgroup=origin_country,
                line=dict(color=color),
                marker=dict(symbol='circle', size=6),
                hovertemplate=f"{origin_country}<br>Date: %{{x}}<br>Total Amount: %{{y:.2f}} (USD)<extra></extra>",
                showlegend=True
            ), row=1, col=1)

            if origin_country not in countries_seen:
                countries_seen.append(origin_country)

    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Total Amount (USD)", row=1, col=1)

    # Fig 2: Total transactions by industry stacked by destination country (bars)
    industry_totals = filtered_data.groupby(['Country', 'Destination Country'])['Amount (USD)'].sum().reset_index()
    
    # Ensure all destination countries are tracked
    for dest_country in industry_totals['Destination Country'].unique():
        if dest_country not in countries_seen:
            countries_seen.append(dest_country)
    
    for des_country in industry_totals['Destination Country'].unique():
        des_country_data = industry_totals[industry_totals['Destination Country'] == des_country]
        iso_code = iso_a3_dict.get(des_country, '')
        color = country_color.get(iso_code, 'black')

        # Show legend for destination countries not already shown in line chart
        show_in_legend = des_country not in country_selected
        
        fig.add_trace(go.Bar(
            x=des_country_data['Country'],
            y=des_country_data['Amount (USD)'] / 1e6,  # Convert to millions
            name=des_country,
            legendgroup=des_country,
            marker=dict(color=color),
            hovertemplate=f"Destination: {des_country}<br>Total Amount: %{{y:.2f}} (Millions USD)<extra></extra>",
            showlegend=show_in_legend
        ), row=2, col=1)

        if des_country not in countries_seen:
            countries_seen.append(des_country)

    fig.update_yaxes(title_text="Total Amount (Millions USD)", row=2, col=1)
    fig.update_xaxes(title_text="Origin Country", row=2, col=1)

    # Fig 3: Scatter plot (spend vs receive)
    send = filtered_data.groupby('Country')['Amount (USD)'].sum().reset_index(name='Spend Amount (USD)')
    receive = filtered_data.groupby('Destination Country')['Amount (USD)'].sum().reset_index(name='Receive Amount (USD)')

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

    # Calculate normalized marker sizes
    if not scatter_data.empty:
        total_amounts = scatter_data['Spend Amount (USD)'] + scatter_data['Receive Amount (USD)']
        if total_amounts.max() > 0:
            # Normalize to range 8-40 for better visibility
            min_size, max_size = 8, 40
            normalized_sizes = min_size + (max_size - min_size) * (total_amounts / total_amounts.max())
        else:
            normalized_sizes = [15] * len(scatter_data)
    else:
        normalized_sizes = []

    # Add scatter by destination country
    for dest_country in scatter_data['Destination Country'].unique():
        scatter_data_country = scatter_data[scatter_data['Destination Country'] == dest_country]
        country_indices = scatter_data['Destination Country'] == dest_country
        country_sizes = normalized_sizes[country_indices] if len(normalized_sizes) > 0 else [15]
        
        iso_code = iso_a3_dict.get(dest_country, '')
        color = country_name_color.get(dest_country, country_color.get(iso_code, 'black'))

        fig.add_trace(go.Scatter(
            x=scatter_data_country['Spend Amount (USD)'] / 1e6,
            y=scatter_data_country['Receive Amount (USD)'] / 1e6,
            mode='markers+text',
            text=scatter_data_country['Destination Country'],
            textfont=dict(size=10, color=color),
            marker=dict(size=country_sizes, color=color, opacity=0.7, symbol='circle'),
            hovertemplate=(
                "Country: %{text}<br>"
                "Spend Amount: %{x:.2f} (Millions USD)<br>"
                "Receive Amount: %{y:.2f} (Millions USD)<extra></extra>"
            ),
            name=dest_country,
            legendgroup=dest_country,
            showlegend=False,  # Don't duplicate
        ), row=2, col=2)

        if dest_country not in countries_seen:
            countries_seen.append(dest_country)

    # Axes and diagonal comparison line for scatter
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

    # Layout
    fig.update_layout(
        height=800,
        title_text="",
        template='plotly_white',
        legend=dict(
            title=dict(text="<b>Countries (Click to Hide/Show)</b>", font=dict(size=14)),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.06)",
            borderwidth=0,
            traceorder='normal'
        ),
        margin=dict(l=8, r=280, t=40, b=40)
    )
    
    # Axis titles
    fig.update_xaxes(title_text=f"Spend Amount (Millions USD)", row=2, col=2)
    fig.update_yaxes(title_text=f"Receive Amount (Millions USD)", row=2, col=2)

    return fig