import dash_cytoscape as cyto
import pandas as pd

def make_shell_network_elements(dataset, risk_range=(0, 10)):
    # Filter for transactions with shell companies and risk range
    df = dataset.copy()
    df = df[df['Shell Companies Involved'] > 0]
    df = df[(df['Money Laundering Risk Score'] >= risk_range[0]) & (df['Money Laundering Risk Score'] <= risk_range[1])]

    nodes = {}
    edges = []

    for _, row in df.iterrows():
        person = row['Person Involved']
        shell = f"Shell_{row['Shell Companies Involved']}"
        country = row['Country']
        risk = row['Money Laundering Risk Score']
        amount = row['Amount (USD)']

        # Add nodes
        if person not in nodes:
            nodes[person] = {'data': {'id': person, 'label': person, 'type': 'person'}}
        if shell not in nodes:
            nodes[shell] = {'data': {'id': shell, 'label': shell, 'type': 'shell'}}
        if country not in nodes:
            nodes[country] = {'data': {'id': country, 'label': country, 'type': 'country'}}

        # Edges: person -> shell, shell -> country
        edge_label = f"Risk: {risk}\nAmount: ${amount:,.0f}"
        edges.append({'data': {'source': person, 'target': shell, 'label': edge_label, 'risk': risk, 'amount': amount}})
        edges.append({'data': {'source': shell, 'target': country, 'label': edge_label, 'risk': risk, 'amount': amount}})

    # Style for node types
    stylesheet = [
        {'selector': 'node[type="person"]', 'style': {'background-color': '#2980b9', 'label': ''}},
        {'selector': 'node[type="shell"]', 'style': {'background-color': '#e67e22', 'label': ''}},
        {'selector': 'node[type="shell"]:selected', 'style': {
            'label': 'data(label)',
            'font-weight': 'bold',
            'font-size': 16,
            'text-background-color': '#fff3cd',
            'text-background-opacity': 1,
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#e67e22',
            'text-border-width': 2,
            'text-border-opacity': 1
        }},
        {'selector': 'node[type="country"]', 'style': {
            'background-color': '#27ae60',
            'label': 'data(label)',
            'font-weight': 'bold',
            'font-size': 16,
            'text-background-color': '#fff3cd',
            'text-background-opacity': 1,
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#27ae60',
            'text-border-width': 2,
            'text-border-opacity': 1
        }},
        {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'label': '', 'font-size': 10}},
        {'selector': 'edge:selected', 'style': {
            'label': 'data(label)',
            'font-weight': 'bold',
            'font-size': 18,
            'line-height': 1.5,
            'text-wrap': 'wrap',
            'text-max-width': 180,
            'text-background-color': '#fff3cd',
            'text-background-opacity': 1,
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#34495e',
            'text-border-width': 2,
            'text-border-opacity': 1,
            'text-halign': 'center',
            'text-valign': 'center',
            'text-margin-y': 4,
            'text-margin-x': 8,
            'padding': '16px',
        }},
    ]

    return list(nodes.values()) + edges, stylesheet
