"""
Callback registration module for the transaction visualization application.
"""
from .navigation_callbacks import register_navigation_callbacks
from .statistical_callbacks import register_statistical_callbacks
from .geographical_callbacks import register_geographical_callbacks
from .industrial_callbacks import register_industrial_callbacks
from .risk_callbacks import register_risk_callbacks


def register_all_callbacks(app):
    """Register all application callbacks"""
    register_navigation_callbacks(app)
    register_statistical_callbacks(app)
    register_geographical_callbacks(app)
    register_industrial_callbacks(app)
    register_risk_callbacks(app)


__all__ = [
    'register_all_callbacks',
    'register_navigation_callbacks',
    'register_statistical_callbacks',
    'register_geographical_callbacks',
    'register_industrial_callbacks',
    'register_risk_callbacks'
]
