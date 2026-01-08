"""
Statistical visualization functions.
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
from dash import dash_table
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Color mappings
color_map_industries = {
    'Arms Trade': "#ed5903",
    'Construction': "#2eaf4d",
    'Luxury Goods': '#ffc107',
    'Casinos': '#17a2b8',
    'Oil & Gas': "#8550e8",
    'Real Estate': "#f23f92",
    'Finance': "#c5e03e",
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


def make_transaction_trends_analysis(dataset):
    """Create comprehensive transaction trends analysis over time"""
    if dataset is None or dataset.empty:
        return go.Figure()
        
    # Convert Date column to datetime for proper handling
    dataset_copy = dataset.copy()
    dataset_copy['Date'] = pd.to_datetime(dataset_copy['Date'])
    dataset_copy['Year_Month'] = dataset_copy['Date'].dt.to_period('M')
    dataset_copy['Is_Illegal'] = (dataset_copy['Source of Money'] == 'Illegal').astype(int)
    
    # Monthly aggregation
    monthly_stats = dataset_copy.groupby(['Year_Month', 'Is_Illegal']).agg({
        'Amount (USD)': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten column names
    monthly_stats.columns = ['Year_Month', 'Is_Illegal', 'Total_Amount', 'Avg_Amount', 'Count']
    monthly_stats['Year_Month_Str'] = monthly_stats['Year_Month'].astype(str)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(' Monthly Transaction Volume ($)', ' Transaction Count by Type', 
                       ' Average Amount by Type', ' Risk Score Trends'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Get legal and illegal data
    legal_data = monthly_stats[monthly_stats['Is_Illegal'] == 0]
    illegal_data = monthly_stats[monthly_stats['Is_Illegal'] == 1]
    
    # Plot 1: Total amount trends
    if not legal_data.empty:
        fig.add_trace(go.Scatter(
            x=legal_data['Year_Month_Str'],
            y=legal_data['Total_Amount'] / 1e6,
            mode='lines+markers',
            name='Legal Transactions',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8)
        ), row=1, col=1)
    
    if not illegal_data.empty:
        fig.add_trace(go.Scatter(
            x=illegal_data['Year_Month_Str'],
            y=illegal_data['Total_Amount'] / 1e6,
            mode='lines+markers',
            name='Illegal Transactions',
            line=dict(color='#DC143C', width=3),
            marker=dict(size=8)
        ), row=1, col=1)
    
    # Plot 2: Transaction counts
    if not legal_data.empty:
        fig.add_trace(go.Bar(
            x=legal_data['Year_Month_Str'],
            y=legal_data['Count'],
            name='Legal Count',
            marker_color='#4682B4',
            opacity=0.8,
            showlegend=False
        ), row=1, col=2)
    
    if not illegal_data.empty:
        fig.add_trace(go.Bar(
            x=illegal_data['Year_Month_Str'],
            y=illegal_data['Count'],
            name='Illegal Count',
            marker_color='#CD5C5C',
            opacity=0.8,
            showlegend=False
        ), row=1, col=2)
    
    # Plot 3: Average amounts
    if not legal_data.empty:
        fig.add_trace(go.Scatter(
            x=legal_data['Year_Month_Str'],
            y=legal_data['Avg_Amount'] / 1e6,
            mode='lines+markers',
            name='Avg Legal',
            line=dict(color='#32CD32', width=2, dash='dash'),
            showlegend=False
        ), row=2, col=1)
    
    if not illegal_data.empty:
        fig.add_trace(go.Scatter(
            x=illegal_data['Year_Month_Str'],
            y=illegal_data['Avg_Amount'] / 1e6,
            mode='lines+markers',
            name='Avg Illegal',
            line=dict(color='#FF6347', width=2, dash='dash'),
            showlegend=False
        ), row=2, col=1)
    
    # Plot 4: Risk score trends
    risk_trends = dataset_copy.groupby('Year_Month')['Money Laundering Risk Score'].agg(['mean', 'std']).reset_index()
    risk_trends['Year_Month_Str'] = risk_trends['Year_Month'].astype(str)
    
    fig.add_trace(go.Scatter(
        x=risk_trends['Year_Month_Str'],
        y=risk_trends['mean'],
        mode='lines+markers',
        name='Average Risk Score',
        line=dict(color='#FF8C00', width=3),
        fill='tonexty',
        fillcolor='rgba(255,140,0,0.1)',
        showlegend=False
    ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        height=700,
        title_text=" Transaction Trends Analysis Over Time",
        title_font_size=24,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=2)
    fig.update_yaxes(title_text="Amount (Millions USD)", row=1, col=1)
    fig.update_yaxes(title_text="Transaction Count", row=1, col=2)
    fig.update_yaxes(title_text="Avg Amount (Millions USD)", row=2, col=1)
    fig.update_yaxes(title_text="Risk Score", row=2, col=2)
    
    return fig


def make_correlation_analysis(dataset):
    """Create correlation analysis heatmap"""
    if dataset is None or dataset.empty:
        return go.Figure()
        
    # Create binary illegal flag for correlation analysis
    dataset_encoded = dataset.copy()
    dataset_encoded['Is_Illegal'] = (dataset_encoded['Source of Money'] == 'Illegal').astype(int)
    
    # Select numeric columns for correlation
    numeric_cols = ['Amount (USD)', 'Money Laundering Risk Score', 'Is_Illegal']
    
    # Encode categorical variables
    from sklearn.preprocessing import LabelEncoder
    le_country = LabelEncoder()
    le_industry = LabelEncoder()
    le_transaction = LabelEncoder()
    
    dataset_encoded['Country_Encoded'] = le_country.fit_transform(dataset_encoded['Country'])
    dataset_encoded['Industry_Encoded'] = le_industry.fit_transform(dataset_encoded['Industry'])
    dataset_encoded['Transaction_Type_Encoded'] = le_transaction.fit_transform(dataset_encoded['Transaction Type'])
    
    # Include encoded variables in correlation
    correlation_cols = numeric_cols + ['Country_Encoded', 'Industry_Encoded', 'Transaction_Type_Encoded']
    
    # Calculate correlation matrix
    corr_matrix = dataset_encoded[correlation_cols].corr()
    
    # Create labels for better readability
    labels = ['Amount (USD)', 'Risk Score', 'Is_Illegal', 'Country', 'Industry', 'Transaction Type']
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale='RdYlBu_r',
        zmid=0,
        colorbar=dict(title="Correlation", titleside="right"),
        hoverongaps=False,
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    # Add correlation values as text
    for i in range(len(corr_matrix)):
        for j in range(len(corr_matrix.columns)):
            fig.add_annotation(
                x=j, y=i,
                text=f'{corr_matrix.iloc[i, j]:.3f}',
                showarrow=False,
                font=dict(color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black', size=12)
            )
    
    fig.update_layout(
        title=' Variable Correlation Analysis',
        title_font_size=20,
        width=600,
        height=500,
        template='plotly_white'
    )
    
    return fig


def make_amount_distribution_analysis(dataset):
    """Create comprehensive amount distribution analysis"""
    if dataset is None or dataset.empty:
        return go.Figure()
        
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(' Amount Distribution by Legality', ' Amount by Industry', 
                       ' Amount by Transaction Type', ' Risk Score Distribution'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Create binary illegal flag for analysis
    dataset_copy = dataset.copy()
    dataset_copy['Is_Illegal'] = (dataset_copy['Source of Money'] == 'Illegal').astype(int)
    
    # Plot 1: Amount distribution by legality
    legal_amounts = dataset_copy[dataset_copy['Is_Illegal'] == 0]['Amount (USD)'] / 1e6
    illegal_amounts = dataset_copy[dataset_copy['Is_Illegal'] == 1]['Amount (USD)'] / 1e6
    
    fig.add_trace(go.Histogram(
        x=legal_amounts,
        name='Legal',
        marker_color='#2E8B57',
        opacity=0.7,
        nbinsx=30
    ), row=1, col=1)
    
    fig.add_trace(go.Histogram(
        x=illegal_amounts,
        name='Illegal',
        marker_color='#DC143C',
        opacity=0.7,
        nbinsx=30
    ), row=1, col=1)
    
    # Plot 2: Amount by industry (box plot)
    industries = dataset['Industry'].unique()
    for i, industry in enumerate(industries):
        industry_data = dataset[dataset['Industry'] == industry]['Amount (USD)'] / 1e6
        color = color_map_industries.get(industry, px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)])
        
        fig.add_trace(go.Box(
            y=industry_data,
            name=industry,
            marker_color=color,
            showlegend=False
        ), row=1, col=2)
    
    # Plot 3: Amount by transaction type
    transaction_types = dataset['Transaction Type'].unique()
    for i, trans_type in enumerate(transaction_types):
        trans_data = dataset[dataset['Transaction Type'] == trans_type]['Amount (USD)'] / 1e6
        
        fig.add_trace(go.Violin(
            y=trans_data,
            name=trans_type,
            side='positive',
            marker_color=px.colors.qualitative.Pastel[i % len(px.colors.qualitative.Pastel)],
            showlegend=False
        ), row=2, col=1)
    
    # Plot 4: Risk score distribution
    fig.add_trace(go.Histogram(
        x=dataset['Money Laundering Risk Score'],
        marker_color='#FF8C00',
        opacity=0.8,
        nbinsx=25,
        showlegend=False
    ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        height=700,
        title_text=" Transaction Amount Distribution Analysis",
        title_font_size=24,
        showlegend=True,
        template='plotly_white'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Amount (Millions USD)", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)
    fig.update_yaxes(title_text="Amount (Millions USD)", row=1, col=2)
    fig.update_yaxes(title_text="Amount (Millions USD)", row=2, col=1)
    fig.update_xaxes(title_text="Risk Score", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    return fig


def make_summary_statistics_table(dataset):
    """Create a comprehensive summary statistics table"""
    if dataset is None or dataset.empty:
        return go.Figure()
        
    # Calculate statistics
    stats = {
        'Metric': [
            'Total Transactions',
            'Total Amount (USD)',
            'Average Amount (USD)',
            'Median Amount (USD)',
            'Standard Deviation',
            'Legal Transactions',
            'Illegal Transactions',
            'Average Risk Score',
            'Countries Involved',
            'Industries Covered',
            'Transaction Types'
        ],
        'Value': [
            f"{len(dataset):,}",
            f"${dataset['Amount (USD)'].sum():,.0f}",
            f"${dataset['Amount (USD)'].mean():,.0f}",
            f"${dataset['Amount (USD)'].median():,.0f}",
            f"${dataset['Amount (USD)'].std():,.0f}",
            f"{len(dataset[dataset['Source of Money'] == 'Legal']):,}",
            f"{len(dataset[dataset['Source of Money'] == 'Illegal']):,}",
            f"{dataset['Money Laundering Risk Score'].mean():.3f}",
            f"{dataset['Country'].nunique()}",
            f"{dataset['Industry'].nunique()}",
            f"{dataset['Transaction Type'].nunique()}"
        ]
    }
    
    # Create table figure
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[' <b>Statistical Metric</b>', ' <b>Value</b>'],
            fill_color='#4472C4',
            font=dict(color='white', size=14),
            align='left',
            height=40
        ),
        cells=dict(
            values=[stats['Metric'], stats['Value']],
            fill_color=[['#f8f9fa', '#e9ecef'] * (len(stats['Metric']) // 2 + 1)][:len(stats['Metric'])],
            font=dict(color='#2c3e50', size=12),
            align='left',
            height=30
        ))
    ])
    
    fig.update_layout(
        title=' Summary Statistics Overview',
        title_font_size=20,
        height=400,
        margin=dict(l=0, r=0, t=50, b=0),
        template='plotly_white'
    )
    
    return fig