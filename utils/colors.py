"""
Color schemes and mappings for the transaction visualization dashboard.
"""

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
    """Get color from colorscale based on amount value."""
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