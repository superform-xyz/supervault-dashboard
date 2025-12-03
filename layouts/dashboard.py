from dash import html, dcc, callback, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from typing import Dict, Any, List

from api.client import SuperVaultApiClient
from components.vault_details import create_vault_details_card
from components.pps_chart import create_pps_chart
from components.tvl_breakdown import create_tvl_breakdown_card
from components.status_cards import create_status_cards
from utils.constants import CHAIN_DATA, DEFAULT_REFRESH_INTERVAL
from utils.formatters import truncate_address

# Use chain data from constants
CHAIN_OPTIONS = [
    {"label": f"{data['name']} ({data['short_name']})", "value": chain_id}
    for chain_id, data in CHAIN_DATA.items()
]

# Function to fetch vault options from the API
def get_vault_options(chain_id: str) -> List[Dict[str, str]]:
    """Fetch available vaults for the selected chain from the API.
    
    Uses the /vaults endpoint which now returns names and symbols directly.
    
    Args:
        chain_id: The blockchain network ID
        
    Returns:
        List of vault option dictionaries with label and value
    """
    client = SuperVaultApiClient()
    try:
        response = client.get_all_vaults(chain_id)
        vaults = response.get("vaults", [])
        names = response.get("names", [])
        symbols = response.get("symbols", [])
        
        if not vaults:
            return []
        
        # Create options list with vault names from the response
        options = []
        for i, vault_address in enumerate(vaults):
            name = names[i] if i < len(names) else "Unknown"
            symbol = symbols[i] if i < len(symbols) else "???"
            label = f"{name} ({symbol})"
            
            options.append({
                "label": label,
                "value": vault_address
            })
        
        return options
    except Exception as e:
        print(f"Error fetching vaults: {e}")
        return []

def create_dashboard_layout():
    """Create the main dashboard layout."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Manager Dashboard", className="text-center mb-4"),
                html.P(
                    "Real-time monitoring and metrics dashboard for SuperVaults.",
                    className="text-center text-muted mb-5"
                ),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Network", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id="chain-selector",
                                    options=CHAIN_OPTIONS,
                                    value="1",  # Default to Ethereum
                                    clearable=False,
                                ),
                            ], md=3),
                            dbc.Col([
                                html.Label("SuperVault", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id="vault-selector",
                                    clearable=False,
                                ),
                                dcc.Loading(
                                    id="loading-vaults",
                                    type="circle",
                                    children=[html.Div()]
                                ),
                            ], md=4),
                            dbc.Col([
                                html.Label("Block Number", className="form-label fw-bold"),
                                dcc.Input(
                                    id="block-number-input",
                                    type="number",
                                    placeholder="Latest",
                                    debounce=True,
                                    style={"width": "100%", "height": "36px"}
                                ),
                            ], md=3),
                            dbc.Col([
                                html.Label("\u00a0", className="form-label"),
                                dbc.Button(
                                    "Refresh Data",
                                    id="refresh-button",
                                    className="w-100 btn-header-green"
                                ),
                            ], md=2),
                        ], className="align-items-end"),
                    ])
                ], className="mb-4"),
            ])
        ]),
        
        # Navigation tabs
        dbc.Tabs([
            dbc.Tab(label="Home", tab_id="tab-home"),
            dbc.Tab(label="Operations", tab_id="tab-operations"),
            dbc.Tab(label="Simulations", tab_id="tab-simulations"),
            dbc.Tab(label="History", tab_id="tab-history"),
        ], id="dashboard-tabs", active_tab="tab-home", className="mb-4"),
        
        # Tab content container
        html.Div(id="tab-content"),
        
        # Hidden divs for storing state
        dcc.Store(id="vault-data-store"),
        
        # Auto-refresh interval (disabled by default to reduce API calls)
        dcc.Interval(
            id="auto-refresh-interval",
            interval=DEFAULT_REFRESH_INTERVAL * 1000,  # Convert to milliseconds
            n_intervals=0,
            disabled=True,  # Manual refresh only
        ),
    ])

# Callback to render tab content
@callback(
    Output("tab-content", "children"),
    Input("dashboard-tabs", "active_tab"),
)
def render_tab_content(active_tab):
    """Render content based on the selected tab."""
    if active_tab == "tab-home":
        return html.Div([
            # Loading container - shown before data loads
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(
                        html.Div("Loading vault data...", className="text-center p-5 text-muted"),
                        color="primary",
                        size="lg",
                    ),
                ], width={"size": 6, "offset": 3}, className="my-5")
            ], id="welcome-container"),
            
            # Main content row
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-vault-details",
                        type="circle",
                        children=[html.Div(id="vault-details-container", className="mb-4")],
                    ),
                ], lg=6),
                dbc.Col([
                    dcc.Loading(
                        id="loading-pps-chart",
                        type="circle",
                        children=[html.Div(id="pps-chart-container", className="mb-4")],
                    ),
                ], lg=6),
            ]),
            
            # TVL breakdown row
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-tvl-breakdown",
                        type="circle",
                        children=[html.Div(id="tvl-breakdown-container", className="mb-4")],
                    ),
                ]),
            ]),
            
            # Fees and Upkeep cards row
            html.Div(id="status-cards-container", className="mb-4"),
        ])
    
    elif active_tab == "tab-operations":
        return dbc.Card([
            dbc.CardBody([
                html.H4("Operations", className="card-title"),
                html.P("Vault operations will be available here.", className="text-muted"),
            ])
        ])
    
    elif active_tab == "tab-simulations":
        return dbc.Card([
            dbc.CardBody([
                html.H4("Simulations", className="card-title"),
                html.P("Simulation tools will be available here.", className="text-muted"),
            ])
        ])
    
    elif active_tab == "tab-history":
        return dbc.Card([
            dbc.CardBody([
                html.H4("History", className="card-title"),
                html.P("Historical data and charts will be available here.", className="text-muted"),
            ])
        ])
    
    return html.Div()


# Callback to update vault options when chain is selected
@callback(
    Output("vault-selector", "options"),
    Output("vault-selector", "value"),
    Output("loading-vaults", "children"),
    Input("chain-selector", "value"),
    prevent_initial_call=False
)
def update_vault_options(selected_chain):
    # Show loading message
    if not selected_chain:
        return [], None, ""
    
    # Fetch vault options from API
    options = get_vault_options(selected_chain)
    value = options[0]["value"] if options else None
    
    # Clear loading message
    return options, value, ""


def create_error_card(error_message):
    """Create an error card to display when an API call fails."""
    return dbc.Card(
        dbc.CardBody([
            html.H5("Error Fetching Data", className="text-danger"),
            html.P(f"An error occurred: {str(error_message)}"),
            html.P("Please try again later or select a different vault.")
        ]),
        className="h-100"
    )

# Callback to update data when the user clicks Refresh, changes selectors, or auto-refresh triggers
@callback(
    Output("status-cards-container", "children"),
    Output("vault-details-container", "children"),
    Output("pps-chart-container", "children"),
    Output("tvl-breakdown-container", "children"),
    Output("welcome-container", "style"),
    Input("refresh-button", "n_clicks"),
    Input("vault-selector", "value"),
    Input("chain-selector", "value"),
    Input("auto-refresh-interval", "n_intervals"),
    State("block-number-input", "value"),
    prevent_initial_call=False
)
def update_dashboard_data(n_clicks, selected_vault, selected_chain, n_intervals, block_number):
    # Check if we have valid selections; otherwise keep the welcome message visible
    if not selected_chain or not selected_vault:
        return html.Div(), html.Div(), html.Div(), html.Div(), {"display": "block"}
    
    # Initialize API client
    client = SuperVaultApiClient()
    
    # If refresh button was clicked, clear cache for this vault to get fresh data
    if ctx.triggered_id == "refresh-button":
        client.clear_vault_cache(selected_chain, selected_vault)
    
    # Parse block number (None if empty or invalid)
    parsed_block = int(block_number) if block_number else None
    
    try:
        # Fetch all vault data in a single call
        vault_data = client.get_vault(selected_chain, selected_vault, parsed_block)
    except Exception as e:
        error_card = create_error_card(str(e))
        return html.Div(), error_card, html.Div(), html.Div(), {"display": "none"}
    
    # Extract asset decimals from vault info (default to 18)
    asset_decimals = 18
    vault_info = vault_data.get("vault", {})
    if "asset" in vault_info and "decimals" in vault_info["asset"]:
        asset_decimals = int(vault_info["asset"]["decimals"])
    
    # Build status cards (alerts, fees, upkeep, managers)
    status_cards = create_status_cards(vault_data, selected_chain)
    
    # Build vault details card
    vault_details_card = create_vault_details_card(vault_data, selected_chain)
    
    # Build PPS chart
    pps_chart = create_pps_chart(vault_data.get("pps", {}), vault_data.get("status", {}), vault_data.get("config", {}))
    
    # Build TVL breakdown
    tvl_breakdown = create_tvl_breakdown_card(vault_data.get("tvl", {}), asset_decimals, selected_chain)
    
    # Hide welcome message
    return status_cards, vault_details_card, pps_chart, tvl_breakdown, {"display": "none"}
