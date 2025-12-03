from typing import Union, Optional

def format_amount(amount: Union[int, float], decimal_places: int = 6) -> str:
    """Format a numeric amount with commas as thousand separators.
    
    Args:
        amount: The numeric amount to format
        decimal_places: Number of decimal places to display
        
    Returns:
        Formatted string representation
    """
    try:
        return f"{float(amount):,.{decimal_places}f}"
    except (ValueError, TypeError):
        return "0.00"

def format_percentage(percentage: Union[int, float], decimal_places: int = 2) -> str:
    """Format a percentage value.
    
    Args:
        percentage: The percentage value to format
        decimal_places: Number of decimal places to display
        
    Returns:
        Formatted percentage string
    """
    try:
        return f"{float(percentage):.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.00%"

def convert_wei_to_eth(wei_amount: Union[int, str], decimals: int = 18) -> float:
    """Convert a wei amount to ETH or other token with specified decimals.
    
    Args:
        wei_amount: Amount in wei (as int or string)
        decimals: Number of decimals for the token
        
    Returns:
        Converted amount as a float
    """
    try:
        wei_amount = int(wei_amount)
        return wei_amount / (10 ** decimals)
    except (ValueError, TypeError):
        return 0.0

def truncate_address(address: str, chars: int = 4) -> str:
    """Truncate an Ethereum address for display.
    
    Args:
        address: The Ethereum address to truncate
        chars: Number of characters to keep at each end
        
    Returns:
        Truncated address string
    """
    if not isinstance(address, str) or len(address) <= 2 * chars:
        return address
    return f"{address[:chars+2]}...{address[-chars:]}"
