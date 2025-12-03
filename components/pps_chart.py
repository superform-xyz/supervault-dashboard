from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import Dict, Any
import time
from datetime import datetime

def get_pps_health_status(last_update_timestamp: int, max_staleness: int, current_time: int) -> tuple:
    """Determine PPS health status based on staleness.
    
    Args:
        last_update_timestamp: When PPS was last updated on-chain
        max_staleness: Maximum allowed staleness in seconds
        current_time: Current timestamp
        
    Returns:
        Tuple of (status_text, status_color, status_icon)
    """
    if max_staleness <= 0:
        return ("Unknown", "#6c757d", "fas fa-question-circle")
    
    age = current_time - last_update_timestamp
    staleness_ratio = age / max_staleness
    
    if staleness_ratio < 0.5:
        return ("Fresh", "#28a745", "fas fa-check-circle")
    elif staleness_ratio < 1.0:
        return ("Warning", "#ffc107", "fas fa-exclamation-triangle")
    else:
        return ("Stale", "#dc3545", "fas fa-times-circle")


def create_pps_chart(pps_data: Dict[str, Any], status_data: Dict[str, Any] = None, config_data: Dict[str, Any] = None) -> dbc.Card:
    """Create a chart component for Price Per Share visualization.
    
    Args:
        pps_data: Dictionary containing PPS data (PPSInfo from /vault/{address})
        status_data: Dictionary containing status info (StatusInfo from /vault/{address})
        config_data: Dictionary containing config info (ConfigInfo from /vault/{address})
        
    Returns:
        A Dash component for the PPS chart
    """
    if status_data is None:
        status_data = {}
    if config_data is None:
        config_data = {}
    
    # Extract data
    current_pps = float(pps_data.get("current_pps", "0"))
    calculated_pps = float(pps_data.get("calculated_pps", "0"))
    last_update_timestamp = pps_data.get("last_update_timestamp", int(time.time()))
    min_update_interval = pps_data.get("min_update_interval", 0)
    max_staleness = pps_data.get("max_staleness", 0)
    
    # Get current timestamp for health calculation
    timestamp = int(time.time())
    
    # Get pps_expiration from config and calculate expiration time
    pps_expiration = config_data.get("pps_expiration", 0)
    expiration_timestamp = last_update_timestamp + pps_expiration if pps_expiration else 0
    expiration_time = datetime.fromtimestamp(expiration_timestamp).strftime('%Y-%m-%d %H:%M:%S') if expiration_timestamp else 'N/A'
    
    # Check if PPS is marked stale from status
    is_pps_stale = status_data.get("is_pps_stale", False) if status_data else False
    
    # Get health status - override if explicitly stale
    if is_pps_stale:
        health_status, health_color, health_icon = ("Stale", "#dc3545", "fas fa-times-circle")
    else:
        health_status, health_color, health_icon = get_pps_health_status(
            last_update_timestamp, max_staleness, timestamp
        )
    
    # For a real dashboard, we would have historical data to plot
    # Here we're creating a simple chart with just the current values
    
    # Convert timestamps to readable format
    current_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    last_update_time = datetime.fromtimestamp(last_update_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Create a figure with two data points
    fig = go.Figure()
    
    # Add current_pps point
    fig.add_trace(go.Scatter(
        x=[current_time],
        y=[current_pps],
        mode='markers',
        name='Current PPS',
        marker=dict(color='blue', size=12)
    ))
    
    # Add calculated_pps point
    fig.add_trace(go.Scatter(
        x=[current_time],
        y=[calculated_pps],
        mode='markers',
        name='Calculated PPS',
        marker=dict(color='green', size=12)
    ))
    
    # Update layout
    fig.update_layout(
        title='Price Per Share (PPS)',
        xaxis_title='Time',
        yaxis_title='PPS Value',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    
    
    # Calculate PPS difference as percentage
    if current_pps > 0:
        pps_diff_pct = (calculated_pps - current_pps) / current_pps * 100
        pps_diff_color = "text-danger" if abs(pps_diff_pct) > 1 else "text-muted"
    else:
        pps_diff_pct = 0
        pps_diff_color = "text-muted"
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H4("Price Per Share (PPS)", className="card-title mb-0"),
                html.Div([
                    html.I(className=f"{health_icon} me-1", style={"color": health_color}),
                    html.Span(health_status, style={"color": health_color, "fontWeight": "bold"})
                ], className="d-flex align-items-center", title=f"Max staleness: {max_staleness}s")
            ], className="d-flex justify-content-between align-items-center"),
            html.H6(f"Last Updated: {last_update_time}", className="card-subtitle text-muted mt-1"),
        ]),
        dbc.CardBody([
            dcc.Graph(
                figure=fig,
                style={'height': 250},
                config={'displayModeBar': False},
            ),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P([
                            html.Span("Current PPS: ", className="fw-bold"),
                            html.Span(f"{current_pps:.6f}", className="text-monospace", **{"data-clipboard-text": str(current_pps)})
                        ], className="mb-1"),
                        html.P([
                            html.Span("Calculated PPS: ", className="fw-bold"),
                            html.Span(f"{calculated_pps:.6f}", className="text-monospace", **{"data-clipboard-text": str(calculated_pps)})
                        ], className="mb-1"),
                        html.P([
                            html.Span("PPS Delta: ", className="fw-bold"),
                            html.Span(f"{pps_diff_pct:.2f}%", className=pps_diff_color)
                        ], className="mb-1"),
                    ], md=6),
                    dbc.Col([
                        html.P([
                            html.Span("Min Update Interval: ", className="fw-bold"),
                            html.Span(f"{min_update_interval}s")
                        ], className="mb-1"),
                        html.P([
                            html.Span("Max Staleness: ", className="fw-bold"),
                            html.Span(f"{max_staleness}s")
                        ], className="mb-1"),
                    ], md=6),
                ]),
            ], className="mt-2"),
        ]),
        dbc.CardFooter([
            html.Small([
                f"Expires: {expiration_time}",
            ], className="text-muted"),
        ]),
    ], className="h-100")
