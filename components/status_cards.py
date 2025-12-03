"""Status cards component for displaying alerts, fees, upkeep, and manager info."""

from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, Any, List
from utils.formatters import convert_wei_to_eth
from utils.constants import get_explorer_address_url



def create_fees_card(fees_data: Dict[str, Any], asset_decimals: int = 18) -> dbc.Card:
    """Create a card showing fee configuration and unrealized profit.
    
    Args:
        fees_data: Dictionary containing fee info
        asset_decimals: Decimals for formatting amounts
        
    Returns:
        A Dash card component for fees
    """
    performance_fee = fees_data.get("performance_fee_bps", 0)
    management_fee = fees_data.get("management_fee_bps", 0)
    recipient = fees_data.get("recipient", "N/A")
    vault_hwm_pps = fees_data.get("vault_hwm_pps", "0")
    unrealized_profit = float(fees_data.get("unrealized_profit", "0"))
    
    # Convert bps to percentage
    perf_fee_pct = performance_fee / 100
    mgmt_fee_pct = management_fee / 100
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Fees", className="card-title mb-0"),
        ]),
        dbc.CardBody([
            html.P([
                html.Span("Performance: ", className="fw-bold"),
                html.Span(f"{perf_fee_pct:.1f}%")
            ], className="mb-1"),
            html.P([
                html.Span("Management: ", className="fw-bold"),
                html.Span(f"{mgmt_fee_pct:.2f}%")
            ], className="mb-1"),
            html.P([
                html.Span("HWM PPS: ", className="fw-bold"),
                html.Span(f"{float(vault_hwm_pps):.6f}")
            ], className="mb-1"),
            html.P([
                html.Span("Unrealized Profit: ", className="fw-bold"),
                html.Span(f"{convert_wei_to_eth(unrealized_profit, asset_decimals):.4f}")
            ], className="mb-0"),
        ])
    ], className="h-100")


def create_upkeep_card(upkeep_data: Dict[str, Any]) -> dbc.Card:
    """Create a card showing upkeep balance.
    
    Args:
        upkeep_data: Dictionary containing upkeep info
        
    Returns:
        A Dash card component for upkeep
    """
    balance = float(upkeep_data.get("balance", "0"))
    balance_formatted = convert_wei_to_eth(balance, 18)
    
    # Determine status color based on balance
    if balance < 1e17:  # < 0.1 ETH
        balance_color = "text-danger"
        status = "Low"
    elif balance < 1e18:  # < 1 ETH
        balance_color = "text-warning"
        status = "Medium"
    else:
        balance_color = "text-success"
        status = "Good"
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Upkeep", className="card-title mb-0"),
        ]),
        dbc.CardBody([
            html.P([
                html.Span("Balance: ", className="fw-bold"),
                html.Span(f"{balance_formatted:.4f} UP")
            ], className="mb-1"),
            html.P([
                html.Span("Status: ", className="fw-bold"),
                html.Span(status, className=balance_color)
            ], className="mb-0"),
        ])
    ], className="h-100")


def create_managers_card(managers_data: Dict[str, Any], chain_id: str = "1") -> dbc.Card:
    """Create a card showing manager information.
    
    Args:
        managers_data: Dictionary containing manager info
        chain_id: Chain ID for explorer links
        
    Returns:
        A Dash card component for managers
    """
    main_manager = managers_data.get("main", "N/A")
    secondary_managers = managers_data.get("secondary", [])
    
    def truncate_addr(addr: str) -> str:
        if len(addr) > 12:
            return f"{addr[:6]}...{addr[-4:]}"
        return addr
    
    main_link = html.A(
        truncate_addr(main_manager),
        href=get_explorer_address_url(chain_id, main_manager),
        target="_blank",
        className="text-decoration-none text-monospace text-dark"
    ) if main_manager != "N/A" else "N/A"
    
    secondary_links = []
    for addr in secondary_managers:
        secondary_links.append(
            html.A(
                truncate_addr(addr),
                href=get_explorer_address_url(chain_id, addr),
                target="_blank",
                className="text-decoration-none text-monospace text-dark me-2"
            )
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Managers", className="card-title mb-0"),
        ]),
        dbc.CardBody([
            html.P([
                html.Span("Main: ", className="fw-bold"),
                main_link
            ], className="mb-1"),
            html.P([
                html.Span("Secondary: ", className="fw-bold"),
                html.Span(secondary_links if secondary_links else "None")
            ], className="mb-0") if secondary_managers else html.P([
                html.Span("Secondary: ", className="fw-bold"),
                html.Span("None")
            ], className="mb-0"),
        ])
    ], className="h-100")


def create_config_card(config_data: Dict[str, Any]) -> dbc.Card:
    """Create a card showing strategy configuration.
    
    Args:
        config_data: Dictionary containing config info
        
    Returns:
        A Dash card component for configuration
    """
    deviation_threshold = config_data.get("deviation_threshold", "0")
    pps_expiration = config_data.get("pps_expiration", 0)
    
    # Convert deviation threshold from 1e18 scale to percentage
    try:
        deviation_pct = float(deviation_threshold) / 1e16  # 1e18 -> percentage
    except (ValueError, TypeError):
        deviation_pct = 0
    
    # Convert pps_expiration to hours
    pps_exp_hours = pps_expiration / 3600 if pps_expiration else 0
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-cog me-2"),
                "Config"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            html.P([
                html.Span("Deviation Threshold: ", className="text-muted"),
                html.Span(f"{deviation_pct:.1f}%", className="fw-bold")
            ], className="mb-2"),
            html.P([
                html.Span("PPS Expiration: ", className="text-muted"),
                html.Span(f"{pps_exp_hours:.1f}h", className="fw-bold")
            ], className="mb-0"),
        ])
    ], className="h-100")


def create_status_cards(vault_data: Dict[str, Any], chain_id: str = "1") -> dbc.Row:
    """Create a row of status cards showing alerts, fees, upkeep, and managers.
    
    Args:
        vault_data: Full vault response from /vault/{address}
        chain_id: Chain ID for explorer links
        
    Returns:
        A Dash Row component containing all status cards
    """
    status_data = vault_data.get("status", {})
    fees_data = vault_data.get("fees", {})
    upkeep_data = vault_data.get("upkeep", {})
    managers_data = vault_data.get("managers", {})
    config_data = vault_data.get("config", {})
    
    # Get asset decimals for formatting
    vault_info = vault_data.get("vault", {})
    asset = vault_info.get("asset", {})
    asset_decimals = asset.get("decimals", 18)
    
    return dbc.Row([
        dbc.Col([
            create_fees_card(fees_data, asset_decimals)
        ], lg=6, md=6, className="mb-3"),
        dbc.Col([
            create_upkeep_card(upkeep_data)
        ], lg=6, md=6, className="mb-3"),
    ])
