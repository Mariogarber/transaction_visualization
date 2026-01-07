"""
Base plotting utilities and common functions for all visualizations.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.colors import _normalize_color_for_plotly


def make_cards_for_industries(filtered_data,
                              palette='Viridis',
                              mode='categorical',
                              height=500,
                              color_map=None,
                              top_n=None,
                              hide_legend=True):
    """
    Create industry cards visualization.
    """
    # Group by industry and calculate relevant metrics
    industry_agg = filtered_data.groupby('Industry').agg({
        'Amount (USD)': 'sum',
        'Transaction ID': 'count'
    }).reset_index()
    industry_agg.columns = ['Industry', 'Total_Amount', 'Transaction_Count']
    industry_agg = industry_agg.sort_values('Total_Amount', ascending=False)
    
    if top_n:
        industry_agg = industry_agg.head(top_n)
    
    # Create cards HTML
    cards = []
    for _, row in industry_agg.iterrows():
        card_content = dbc.Card([
            dbc.CardBody([
                html.H4(row['Industry'], 
                       style={'color': '#2c3e50', 'fontWeight': '700', 'marginBottom': '15px'}),
                html.P([
                    html.Span("💰 ", style={'fontSize': '18px'}),
                    html.Strong(f"${row['Total_Amount']:,.0f}", 
                               style={'color': '#e74c3c', 'fontSize': '20px'})
                ], style={'marginBottom': '10px'}),
                html.P([
                    html.Span("📊 ", style={'fontSize': '16px'}),
                    f"{row['Transaction_Count']} transactions"
                ], style={'color': '#5a6c7d', 'marginBottom': '0'})
            ])
        ], style={'borderLeft': '4px solid #3498db', 'marginBottom': '15px'})
        
        cards.append(dbc.Col([card_content], width=6, lg=4))
    
    return dbc.Row(cards)