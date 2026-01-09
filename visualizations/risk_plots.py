"""
Risk analysis visualization functions.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def make_risk_distribution_analysis(dataset):
    """Create risk score distribution analysis with histogram and box plots"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Risk Score Distribution by Source',
            'Risk Score Box Plot by Source', 
            'Risk Score Histogram Overlay',
            'Risk Score Statistics'
        ),
        specs=[
            [{'type': 'histogram'}, {'type': 'box'}],
            [{'type': 'histogram'}, {'type': 'table'}]
        ]
    )
    
    # Separate legal and illegal data
    legal_data = dataset[dataset['Source of Money'] == 'Legal']
    illegal_data = dataset[dataset['Source of Money'] == 'Illegal']
    
    # 1. Histogram by source (subplot 1)
    fig.add_trace(
        go.Histogram(
            x=illegal_data['Money Laundering Risk Score'],
            name='Illegal',
            marker_color='#E74C3C',
            opacity=0.7,
            nbinsx=10,
            legendgroup='Illegal',
            showlegend=True
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Histogram(
            x=legal_data['Money Laundering Risk Score'],
            name='Legal',
            marker_color='#32CD32',
            opacity=0.7,
            nbinsx=10,
            legendgroup='Legal',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # 2. Box plots (subplot 2)
    fig.add_trace(
        go.Box(
            y=legal_data['Money Laundering Risk Score'],
            name='Legal',
            marker_color='#32CD32',
            boxpoints='outliers',
            legendgroup='Legal',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Box(
            y=illegal_data['Money Laundering Risk Score'],
            name='Illegal', 
            marker_color='#E74C3C',
            boxpoints='outliers',
            legendgroup='Illegal',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Combined histogram (subplot 3)
    fig.add_trace(
        go.Histogram(
            x=dataset['Money Laundering Risk Score'],
            name='All Transactions',
            marker_color='#9B59B6',
            opacity=0.8,
            nbinsx=10,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Statistics table (subplot 4)
    stats_data = {
        'Metric': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'],
        'Legal': [
            len(legal_data),
            round(legal_data['Money Laundering Risk Score'].mean(), 2),
            legal_data['Money Laundering Risk Score'].median(),
            round(legal_data['Money Laundering Risk Score'].std(), 2),
            legal_data['Money Laundering Risk Score'].min(),
            legal_data['Money Laundering Risk Score'].max()
        ],
        'Illegal': [
            len(illegal_data),
            round(illegal_data['Money Laundering Risk Score'].mean(), 2),
            illegal_data['Money Laundering Risk Score'].median(),
            round(illegal_data['Money Laundering Risk Score'].std(), 2),
            illegal_data['Money Laundering Risk Score'].min(),
            illegal_data['Money Laundering Risk Score'].max()
        ]
    }
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=['<b>Metric</b>', '<b>Legal</b>', '<b>Illegal</b>'],
                fill_color='#34495E',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[stats_data['Metric'], stats_data['Legal'], stats_data['Illegal']],
                fill_color='#ECF0F1',
                font=dict(size=11)
            )
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='<b>Risk Score Distribution Analysis</b>',
        title_x=0.5,
        height=800,
        showlegend=True,
        barmode='overlay'
    )
    
    # Update axis labels
    fig.update_xaxes(title_text='Risk Score', row=1, col=1)
    fig.update_yaxes(title_text='Count', row=1, col=1)
    fig.update_yaxes(title_text='Risk Score', row=1, col=2)
    fig.update_xaxes(title_text='Risk Score', row=2, col=1)
    fig.update_yaxes(title_text='Count', row=2, col=1)
    
    return fig


def make_transaction_amount_analysis(dataset, use_clustering=False):
    """Create transaction amount vs risk score analysis with interactive scatter plot"""
    # Check if dataset is empty
    if len(dataset) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected industries",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="<b>Transaction Amount vs Risk Score Analysis</b>",
            title_x=0.5,
            xaxis=dict(title="Money Laundering Risk Score", range=[0.5, 10.5]),
            yaxis=dict(title="Amount (Log10 USD)"),
            height=900  # Increased height
        )
        return fig
    
    # Add log amount for better visualization
    dataset_copy = dataset.copy()
    dataset_copy['Log Amount'] = np.log10(dataset_copy['Amount (USD)'])
    
    # Apply clustering if requested
    if use_clustering:
        clustered_data = []
        
        # Group by Industry and Source of Money for clustering
        for (industry, source), group in dataset_copy.groupby(['Industry', 'Source of Money']):
            if len(group) > 1:  # Only cluster if we have multiple points
                # Determine number of clusters (max 10, or sqrt of group size)
                n_clusters = min(10, max(1, int(np.sqrt(len(group)))))
                
                # Features for clustering: Risk Score and Log Amount
                features = group[['Money Laundering Risk Score', 'Log Amount']].values
                
                # Apply KMeans clustering
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(features)
                
                # Create centroids with aggregated information
                for i in range(n_clusters):
                    cluster_mask = clusters == i
                    cluster_group = group[cluster_mask]
                    
                    if len(cluster_group) > 0:
                        centroid_data = {
                            'Money Laundering Risk Score': cluster_group['Money Laundering Risk Score'].mean(),
                            'Log Amount': cluster_group['Log Amount'].mean(),
                            'Amount (USD)': cluster_group['Amount (USD)'].mean(),
                            'Shell Companies Involved': cluster_group['Shell Companies Involved'].mean(),
                            'Industry': industry,
                            'Source of Money': source,
                            'Country': f"{len(cluster_group)} transactions",
                            'Destination Country': f"Avg: {cluster_group['Amount (USD)'].mean():.0f} USD",
                            'Transaction Type': f"Cluster {i+1}",
                            'Cluster_Size': len(cluster_group),
                            'Original_Count': len(cluster_group)
                        }
                        clustered_data.append(centroid_data)
            else:
                # Keep single points as is
                for _, row in group.iterrows():
                    row_dict = row.to_dict()
                    row_dict['Cluster_Size'] = 1
                    row_dict['Original_Count'] = 1
                    clustered_data.append(row_dict)
        
        # Convert to DataFrame
        plot_data = pd.DataFrame(clustered_data)
        title_suffix = " (Clustered View)"
        size_column = 'Cluster_Size'
    else:
        plot_data = dataset_copy
        title_suffix = ""
        size_column = 'Shell Companies Involved'
    
    # Create scatter plot
    fig = px.scatter(
        plot_data,
        x='Money Laundering Risk Score',
        y='Log Amount',
        color='Source of Money',
        symbol='Industry',
        size=size_column,
        hover_data=['Country', 'Destination Country', 'Transaction Type', 'Amount (USD)'],
        color_discrete_map={'Legal': '#32CD32', 'Illegal': '#E74C3C'},
        title=f'<b>Transaction Amount vs Risk Score Analysis{title_suffix}</b>',
        labels={
            'Money Laundering Risk Score': 'Money Laundering Risk Score',
            'Log Amount': 'Amount (Log10 USD)',
            'Source of Money': 'Source'
        }
    )
    
    # Only add trendlines if we have enough data
    if len(plot_data) >= 2:
        # Add trendlines
        legal_data = plot_data[plot_data['Source of Money'] == 'Legal']
        illegal_data = plot_data[plot_data['Source of Money'] == 'Illegal']
        
        # Calculate trendlines only if we have data for each category
        x_trend = np.linspace(1, 10, 100)
        
        if len(legal_data) >= 2:
            legal_z = np.polyfit(legal_data['Money Laundering Risk Score'], legal_data['Log Amount'], 1)
            legal_p = np.poly1d(legal_z)
            
            fig.add_trace(
                go.Scatter(
                    x=x_trend,
                    y=legal_p(x_trend),
                    mode='lines',
                    name='Legal Trend',
                    line=dict(color='#32CD32', width=3, dash='dash')
                )
            )
        
        if len(illegal_data) >= 2:
            illegal_z = np.polyfit(illegal_data['Money Laundering Risk Score'], illegal_data['Log Amount'], 1)
            illegal_p = np.poly1d(illegal_z)
            
            fig.add_trace(
                go.Scatter(
                    x=x_trend,
                    y=illegal_p(x_trend),
                    mode='lines',
                    name='Illegal Trend',
                    line=dict(color='#E74C3C', width=3, dash='dash')
                )
            )
    
    # Update layout
    fig.update_layout(
        title_x=0.5,
        height=600,
        xaxis=dict(range=[0.5, 10.5]),
        yaxis=dict(title='Transaction Amount (Log10 USD)'),
        legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1)
    )
    
    # Add summary statistics annotation
    if use_clustering and 'Original_Count' in plot_data.columns:
        total_transactions = plot_data['Original_Count'].sum()
        clusters_count = len(plot_data)
        reduction_ratio = (total_transactions - clusters_count) / total_transactions * 100
        stat_text = f" Clustered: {clusters_count} centroids from {total_transactions:,} transactions ({reduction_ratio:.1f}% reduction)"
    else:
        total_transactions = len(plot_data)
        stat_text = f" Showing {total_transactions:,} transactions"
    
    industries_count = plot_data['Industry'].nunique()
    legal_count = len(plot_data[plot_data['Source of Money'] == 'Legal'])
    illegal_count = len(plot_data[plot_data['Source of Money'] == 'Illegal'])
    
    stat_text += f" | {industries_count} industries | Legal: {legal_count:,} | Illegal: {illegal_count:,}"
    
    fig.add_annotation(
        text=stat_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        xanchor='center', yanchor='top',
        showarrow=False,
        font=dict(size=12, color="#7f8c8d"),
        bgcolor="rgba(248, 249, 250, 0.8)",
        bordercolor="#dee2e6",
        borderwidth=1
    )
    
    return fig


def make_shell_companies_analysis(dataset):
    """Create shell companies analysis by industry with stacked bars"""
    # Group by industry and source, get shell company stats
    grouped = dataset.groupby(['Industry', 'Source of Money']).agg({
        'Shell Companies Involved': ['mean', 'sum', 'count'],
        'Amount (USD)': 'sum'
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['Industry', 'Source', 'Mean_Shell', 'Total_Shell', 'Count', 'Total_Amount']
    
    # Create pivot for easier plotting
    shell_mean = grouped.pivot(index='Industry', columns='Source', values='Mean_Shell').fillna(0)
    shell_total = grouped.pivot(index='Industry', columns='Source', values='Total_Shell').fillna(0)
    count_trans = grouped.pivot(index='Industry', columns='Source', values='Count').fillna(0)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Average Shell Companies by Industry',
            'Total Shell Companies by Industry',
            'Transaction Count by Industry',
            'Shell Company Usage Rate'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'bar'}, {'type': 'bar'}]
        ]
    )
    
    industries = shell_mean.index
    
    # 1. Average shell companies
    fig.add_trace(
        go.Bar(
            x=industries,
            y=shell_mean['Legal'] if 'Legal' in shell_mean.columns else [0]*len(industries),
            name='Legal (Avg)',
            marker_color='#32CD32',
            opacity=0.8,
            legendgroup='Legal',
            showlegend=True
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=industries,
            y=shell_mean['Illegal'] if 'Illegal' in shell_mean.columns else [0]*len(industries),
            name='Illegal (Avg)',
            marker_color='#E74C3C',
            opacity=0.8,
            legendgroup='Illegal',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # 2. Total shell companies
    fig.add_trace(
        go.Bar(
            x=industries,
            y=shell_total['Legal'] if 'Legal' in shell_total.columns else [0]*len(industries),
            name='Legal (Total)',
            marker_color='#32CD32',
            opacity=0.8,
            showlegend=False,
            legendgroup='Legal'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=industries,
            y=shell_total['Illegal'] if 'Illegal' in shell_total.columns else [0]*len(industries),
            name='Illegal (Total)',
            marker_color='#E74C3C',
            opacity=0.8,
            showlegend=False,
            legendgroup='Illegal'
        ),
        row=1, col=2
    )
    
    # 3. Transaction count
    fig.add_trace(
        go.Bar(
            x=industries,
            y=count_trans['Legal'] if 'Legal' in count_trans.columns else [0]*len(industries),
            name='Legal (Count)',
            marker_color='#32CD32',
            opacity=0.8,
            showlegend=False,
            legendgroup='Legal'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=industries,
            y=count_trans['Illegal'] if 'Illegal' in count_trans.columns else [0]*len(industries),
            name='Illegal (Count)',
            marker_color='#E74C3C',
            opacity=0.8,
            showlegend=False,
            legendgroup='Illegal'
        ),
        row=2, col=1
    )
    
    # 4. Shell company usage rate (shell companies per transaction)
    legal_rate = (shell_total['Legal'] / count_trans['Legal']).fillna(0) if 'Legal' in shell_total.columns else [0]*len(industries)
    illegal_rate = (shell_total['Illegal'] / count_trans['Illegal']).fillna(0) if 'Illegal' in shell_total.columns else [0]*len(industries)
    
    fig.add_trace(
        go.Bar(
            x=industries,
            y=legal_rate,
            name='Legal (Rate)',
            marker_color='#32CD32',
            opacity=0.8,
            showlegend=False,
            legendgroup='Legal'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=industries,
            y=illegal_rate,
            name='Illegal (Rate)',
            marker_color='#E74C3C',
            opacity=0.8,
            showlegend=False,
            legendgroup='Illegal'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='<b>Shell Companies Analysis by Industry</b>',
        title_x=0.5,
        height=800,
        showlegend=True,
        barmode='group'
    )
    
    # Update axis labels and rotate x-axis labels
    for row in [1, 2]:
        for col in [1, 2]:
            fig.update_xaxes(tickangle=45, row=row, col=col)
    
    fig.update_yaxes(title_text='Avg Shell Companies', row=1, col=1)
    fig.update_yaxes(title_text='Total Shell Companies', row=1, col=2)
    fig.update_yaxes(title_text='Transaction Count', row=2, col=1)
    fig.update_yaxes(title_text='Shell Companies per Transaction', row=2, col=2)
    
    return fig


def make_tax_haven_flow_analysis(dataset):
    """Create tax haven flow analysis using Sankey diagram"""
    # Create flow data: Source Country -> Destination Country -> Tax Haven
    flow_data = dataset.groupby(['Country', 'Destination Country', 'Tax Haven Country']).agg({
        'Amount (USD)': 'sum',
        'Transaction ID': 'count'
    }).reset_index()
    
    # Create nodes
    countries = sorted(dataset['Country'].unique())
    destinations = sorted(dataset['Destination Country'].unique())
    tax_havens = sorted(dataset['Tax Haven Country'].unique())
    
    # Create unique node list
    all_nodes = []
    node_colors = []
    
    # Source countries (blue)
    for country in countries:
        all_nodes.append(f"Source: {country}")
        node_colors.append('#3498DB')
    
    # Destination countries (green)
    for country in destinations:
        all_nodes.append(f"Dest: {country}")
        node_colors.append('#2ECC71')
    
    # Tax havens (red)
    for haven in tax_havens:
        all_nodes.append(f"Haven: {haven}")
        node_colors.append('#E74C3C')
    
    # Create node mapping
    node_map = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Create links
    source_indices = []
    target_indices = []
    values = []
    link_colors = []
    
    # Links from source to destination
    src_dest = flow_data.groupby(['Country', 'Destination Country'])['Amount (USD)'].sum().reset_index()
    for _, row in src_dest.iterrows():
        source_idx = node_map[f"Source: {row['Country']}"]
        target_idx = node_map[f"Dest: {row['Destination Country']}"]
        source_indices.append(source_idx)
        target_indices.append(target_idx)
        values.append(row['Amount (USD)'])
        link_colors.append('rgba(52, 152, 219, 0.3)')
    
    # Links from destination to tax haven
    dest_haven = flow_data.groupby(['Destination Country', 'Tax Haven Country'])['Amount (USD)'].sum().reset_index()
    for _, row in dest_haven.iterrows():
        source_idx = node_map[f"Dest: {row['Destination Country']}"]
        target_idx = node_map[f"Haven: {row['Tax Haven Country']}"]
        source_indices.append(source_idx)
        target_indices.append(target_idx)
        values.append(row['Amount (USD)'])
        link_colors.append('rgba(231, 76, 60, 0.3)')
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors
        )
    )])
    
    fig.update_layout(
        title_text='<b>Money Flow Analysis: Source Countries → Destinations → Tax Havens</b>',
        title_x=0.5,
        font_size=10,
        height=700
    )
    
    return fig