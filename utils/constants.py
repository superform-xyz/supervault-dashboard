"""
Constants used throughout the SuperVault Dashboard application.
"""
from utils.config import Config

# API base URL (from config, environment-aware)
API_BASE_URL = Config.API_BASE_URL

# Default refresh interval in seconds
DEFAULT_REFRESH_INTERVAL = Config.REFRESH_INTERVAL

# Sample chain data for development
CHAIN_DATA = {
    "1": {
        "name": "Ethereum",
        "short_name": "ETH",
        "logo": "ethereum.png",
        "explorer": "https://etherscan.io"
    }
}

def get_explorer_address_url(chain_id: str, address: str) -> str:
    """Get the block explorer URL for an address on a given chain.
    
    Args:
        chain_id: The chain ID
        address: The Ethereum address
        
    Returns:
        Full URL to the address on the block explorer
    """
    chain_data = CHAIN_DATA.get(chain_id, CHAIN_DATA.get("1"))
    explorer = chain_data.get("explorer", "https://etherscan.io")
    return f"{explorer}/address/{address}"
