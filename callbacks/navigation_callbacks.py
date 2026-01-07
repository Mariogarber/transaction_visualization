"""
Navigation and routing callbacks.
"""
from dash import Input, Output, no_update, callback_context


def register_navigation_callbacks(app):
    """Register navigation and routing callbacks"""
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        """Route to different pages based on URL pathname"""
        from layouts.statistical_layout import create_statistical_layout
        from layouts.geographical_layout import create_geographical_layout
        from layouts.industrial_layout import create_industrial_layout
        from layouts.risk_layout import create_risk_layout
        from layouts.base_layout import create_main_layout
        
        data_manager = app.data_manager
        data = data_manager.get_data()
        
        if pathname == '/statistical' or pathname == '/':
            return create_statistical_layout(data)
        elif pathname == '/geographical':
            return create_geographical_layout(data)
        elif pathname == '/industrial':
            return create_industrial_layout(data)
        elif pathname == '/risk':
            return create_risk_layout(data)
        else:
            return create_statistical_layout(data)

    @app.callback(
        Output('url', 'pathname'),
        Input('nav-statistical', 'n_clicks'),
        Input('nav-geographical', 'n_clicks'),
        Input('nav-industrial', 'n_clicks'),
        Input('nav-risk-analysis', 'n_clicks')
    )
    def navigate_pages(nav_statistical_clicks, nav_geographical_clicks, nav_industrial_clicks, nav_risk_clicks):
        """Handle navigation button clicks"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'nav-statistical':
            return '/statistical'
        elif trigger_id == 'nav-geographical':
            return '/geographical'
        elif trigger_id == 'nav-industrial':
            return '/industrial'
        elif trigger_id == 'nav-risk-analysis':
            return '/risk'
        
        return no_update
