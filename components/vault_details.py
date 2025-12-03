from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, Any
from datetime import datetime
from utils.formatters import format_amount, convert_wei_to_eth
from utils.constants import get_explorer_address_url


def create_address_link(address: str, chain_id: str = "1") -> html.A:
    """Create a clickable address link that opens in block explorer.
    
    Args:
        address: The Ethereum address
        chain_id: The chain ID for the block explorer URL
        
    Returns:
        An html.A component with the address
    """
    explorer_url = get_explorer_address_url(chain_id, address)
    return html.A(
        address,
        href=explorer_url,
        target="_blank",
        className="address-link text-monospace",
        title=f"View on block explorer: {address}",
        **{"data-clipboard-text": address}
    )


def create_vault_details_card(vault_data: Dict[str, Any], chain_id: str = "1") -> dbc.Card:
    """Create a card component displaying vault details.
    
    Args:
        vault_data: Dictionary containing full vault response from /vault/{address}
        chain_id: The chain ID for block explorer links
        
    Returns:
        A Dash component for the vault details card
    """
    # Extract vault info from nested structure
    vault_info = vault_data.get("vault", {})
    status_info = vault_data.get("status", {})
    managers_info = vault_data.get("managers", {})
    
    vault_address = vault_info.get("address", "N/A")
    vault_name = vault_info.get("name", "Unknown Vault")
    vault_symbol = vault_info.get("symbol", "N/A")

    strategy_address = vault_info.get("strategy", "N/A")
    escrow_address = vault_info.get("escrow", "N/A")
    escrowed_assets = vault_info.get("escrowed_assets", "0")
    main_manager = managers_info.get("main", "N/A")
    is_paused = status_info.get("is_paused", False)

    # Get asset details
    asset = vault_info.get("asset", {})
    asset_symbol = asset.get("symbol", "N/A")
    asset_decimals = asset.get("decimals", 18)
    
    # Convert wei amounts to human-readable
    total_assets = vault_info.get("total_assets", 0)
    total_supply = vault_info.get("total_supply", 0)
    
    total_assets_formatted = convert_wei_to_eth(total_assets, asset_decimals)
    total_supply_formatted = convert_wei_to_eth(total_supply, asset_decimals)
    escrowed_formatted = convert_wei_to_eth(escrowed_assets, asset_decimals)
    
    # Status indicator style based on is_paused
    status_indicator_color = "#FFC107" if is_paused else "#28A745"  # Yellow if paused, green if not
    status_indicator_text = "Paused" if is_paused else "Active"
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4(vault_name, className="card-title"),
            html.H6(f"Symbol: {vault_symbol}", className="card-subtitle text-muted"),
        ]),
        dbc.CardBody([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P("Vault Address:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        create_address_link(vault_address, chain_id)
                    ], width=8),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        html.P("Strategy Address:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        create_address_link(strategy_address, chain_id)
                    ], width=8),
                ], className="mb-2"),  
                dbc.Row([
                    dbc.Col([
                        html.P("Escrow Address:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        create_address_link(escrow_address, chain_id)
                    ], width=8),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        html.P("Main Manager:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        create_address_link(main_manager, chain_id)
                    ], width=8),
                ], className="mb-2"),           
                dbc.Row([
                    dbc.Col([
                        html.P("Underlying Asset:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span(asset_symbol, className="me-2"),
                            create_address_link(asset.get("address", ""), chain_id) if asset.get("address") else None
                        ], className="d-flex align-items-center flex-wrap")
                    ], width=8),
                ], className="mb-2"),
                
                dbc.Row([
                    dbc.Col([
                        html.P("Total Assets:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        html.P(f"{total_assets_formatted} {asset_symbol}"),
                    ], width=8),
                ], className="mb-2"),
                
                dbc.Row([
                    dbc.Col([
                        html.P("Total Supply:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        html.P(f"{total_supply_formatted} {vault_symbol}"),
                    ], width=8),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        html.P("Escrowed Assets:", className="fw-bold"),
                    ], width=4),
                    dbc.Col([
                        html.P(f"{escrowed_formatted} {asset_symbol}"),
                    ], width=8),
                ], className="mb-2"),
            ]),
        ]),
        dbc.CardFooter([
            dbc.Row([
                dbc.Col([
                    html.Small([
                        f"Fetched: {datetime.fromtimestamp(vault_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S') if vault_data.get('timestamp') else 'N/A'}",
                        html.Span(" | ", className="mx-1") if vault_data.get('block_number') else "",
                        html.Span(f"Block: {vault_data.get('block_number')}", className="fw-bold") if vault_data.get('block_number') else ""
                    ], className="text-muted"),
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.Span(
                            status_indicator_text,
                            className="me-2"
                        ),
                        html.Div(
                            style={
                                "width": "12px",
                                "height": "12px",
                                "borderRadius": "50%",
                                "backgroundColor": status_indicator_color,
                                "display": "inline-block",
                                "verticalAlign": "middle"
                            }
                        )
                    ], className="d-flex align-items-center justify-content-end")
                ])
            ])
        ]),
    ], className="h-100")
