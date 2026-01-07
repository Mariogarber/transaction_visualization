"""
Constants and configuration for the transaction visualization dashboard.
"""

# Dashboard configuration
DASHBOARD_TITLE = "Money Laundering Transaction Analysis"
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8080

# Country code mapping for choropleth maps
COUNTRY_CODE_MAP = {
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

# Industry risk levels for analysis
INDUSTRY_RISK_LEVELS = {
    'Arms Trade': 9,
    'Casinos': 8, 
    'Real Estate': 7,
    'Finance': 6,
    'Oil & Gas': 5,
    'Luxury Goods': 4,
    'Construction': 3
}

# Transaction type risk levels
TRANSACTION_TYPE_RISK = {
    'Cryptocurrency': 9,
    'Offshore Transfer': 8,
    'Cash Withdrawal': 6,
    'Property Purchase': 5,
    'Stocks Transfer': 4
}