from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from utils.formatters import convert_wei_to_eth, format_percentage
from utils.constants import get_explorer_address_url

def create_tvl_breakdown_card(tvl_data: Dict[str, Any], asset_decimals: int = 18, chain_id: str = "1") -> dbc.Card:
    """Create a chart component for TVL breakdown visualization.
    
    Args:
        tvl_data: Dictionary containing TVL data (TVLInfo from /vault/{address})
        asset_decimals: Number of decimals for the underlying asset
        chain_id: Chain ID for block explorer links
        
    Returns:
        A Dash component for the TVL breakdown chart
    """
    # Extract data - new structure uses 'total' instead of 'calculated_total_assets'
    total_assets = float(tvl_data.get("total", "0"))
    sources = tvl_data.get("sources", [])
    
    if not sources:
        return dbc.Card([
            dbc.CardHeader("Allocation Breakdown"),
            dbc.CardBody([
                html.P("No allocation data available for this vault.", className="text-center text-muted"),
            ]),
        ])
    
    # Create DataFrame for visualization - new structure uses 'assets' instead of 'total_assets'
    df = pd.DataFrame([
        {
            "name": source.get("name", f"Source {i}"),
            "address": source.get("address", ""),
            "oracle": source.get("oracle", ""),
            "value": int(source.get("assets", "0")),
            "percentage": source.get("percentage", 0),
            # Idle assets are not considered active yield sources
            "is_idle": source.get("name", "").startswith("Idle "),
            "is_active": source.get("is_active", True) and not source.get("name", "").startswith("Idle "),
        }
        for i, source in enumerate(sources)
    ])
    
    # Sort by value
    df = df.sort_values("value", ascending=False)
    
    # Create a pie chart for the percentage breakdown
    fig = px.pie(
        df,
        values="percentage",
        names="name",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )
    
    # Create the detailed breakdown table
    table_rows = []
    for _, row in df.iterrows():
        name = row["name"]
        address = row["address"]
        oracle = row["oracle"]
        value = row["value"]
        percentage = row["percentage"]
        is_active = row["is_active"]
        is_idle = row["is_idle"]
        
        # Status badge - Idle assets shown as "Idle", others as Active/Inactive
        if is_idle:
            status_badge = dbc.Badge("Idle", color="secondary", className="me-1")
        else:
            status_badge = dbc.Badge(
                "Active" if is_active else "Inactive",
                color="success" if is_active else "danger",
                className="me-1"
            )
        
        # For idle assets, make the name itself a link to the address (no separate address shown)
        if is_idle and address:
            name_cell = html.A(
                name,
                href=get_explorer_address_url(chain_id, address),
                target="_blank",
                className="text-decoration-none",
                title=address
            )
        elif address:
            # Non-idle: show name with address link
            address_link = html.A(
                f"{address[:6]}...{address[-4:]}" if len(address) > 12 else address,
                href=get_explorer_address_url(chain_id, address),
                target="_blank",
                className="text-decoration-none",
                title=address
            )
            name_cell = [html.Span(name, className="me-2"), address_link]
        else:
            name_cell = name
        
        # Create clickable oracle link
        oracle_link = html.A(
            f"{oracle[:6]}...{oracle[-4:]}" if len(oracle) > 12 else oracle,
            href=get_explorer_address_url(chain_id, oracle),
            target="_blank",
            className="text-decoration-none",
            title=oracle
        ) if oracle else "N/A"
        
        table_rows.append(
            html.Tr([
                html.Td(name_cell),
                html.Td(oracle_link),
                html.Td(f"{convert_wei_to_eth(value, asset_decimals):.4f}"),
                html.Td(f"{percentage:.2f}%"),
                html.Td(status_badge),
            ])
        )
    
    # Count active sources (excluding idle)
    active_count = df["is_active"].sum()
    idle_count = df["is_idle"].sum()
    inactive_count = len(df) - active_count - idle_count
    
    # Create the component
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Allocations", className="card-title"),
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=fig,
                        config={'displayModeBar': False},
                        style={'height': 300},
                    ),
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.H5("Total Assets"),
                        html.H3(f"{convert_wei_to_eth(total_assets, asset_decimals):.4f}"),
                        html.P(f"Across {len(sources)} sources"),
                        html.Div([
                            html.P([
                                html.Span("Active Sources: ", className="fw-bold"),
                                html.Span(str(active_count))
                            ]),
                            html.P([
                                html.Span("Idle: ", className="fw-bold"),
                                html.Span(str(idle_count))
                            ]),
                        ]),
                    ], className="d-flex flex-column justify-content-center h-100"),
                ], md=6),
            ]),
            
            html.Hr(),
            
            html.Div([
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Source"),
                            html.Th("Oracle"),
                            html.Th("Assets"),
                            html.Th("Percentage"),
                            html.Th("Status"),
                        ])
                    ]),
                    html.Tbody(table_rows),
                ], striped=True, bordered=True, hover=True, responsive=True),
            ]),
        ]),
    ])
