import requests
from typing import Dict, Any, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.constants import API_BASE_URL
from utils.config import Config


# Module-level shared cache (persists across client instances)
_shared_cache: Dict[str, tuple] = {}
_cache_ttl = Config.CACHE_TTL


class SuperVaultApiClient:
    """Client for interacting with the SuperVault Pricing API."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5  # seconds between retries
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the SuperVault API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from shared cache if it exists and is not expired."""
        if key in _shared_cache:
            timestamp, data = _shared_cache[key]
            if time.time() - timestamp < _cache_ttl:
                return data
        return None
    
    def _store_in_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Store data in shared cache with current timestamp."""
        _shared_cache[key] = (time.time(), data)
    
    def _request_with_retry(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Make a GET request with retry logic.
        
        Args:
            endpoint: The API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: After MAX_RETRIES failed attempts
        """
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(endpoint, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
        raise last_exception
    
    def get_all_vaults(self, chain_id: str) -> Dict[str, Any]:
        """Get all SuperVaults for a specific chain.
        
        Args:
            chain_id: Blockchain network ID
            
        Returns:
            Dict containing lists of vaults, strategies, and escrows
        """
        cache_key = f"vaults_{chain_id}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        endpoint = f"{self.base_url}/api/v1/vaults"
        params = {"chain_id": chain_id}
        
        data = self._request_with_retry(endpoint, params)
        self._store_in_cache(cache_key, data)
        return data
    
    def get_pps(self, chain_id: str, vault: str, block_number: Optional[int] = None) -> Dict[str, Any]:
        """Get current PPS (Price Per Share) for a specific SuperVault.
        
        Args:
            chain_id: Blockchain network ID
            vault: SuperVault address
            block_number: Optional block number for historical query
            
        Returns:
            Dict containing PPS data
        """
        cache_key = f"pps_{chain_id}_{vault}_{block_number or 'latest'}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        endpoint = f"{self.base_url}/api/v1/pps"
        params = {"chain_id": chain_id, "vault": vault}
        if block_number is not None:
            params["block_number"] = str(block_number)
        
        data = self._request_with_retry(endpoint, params)
        self._store_in_cache(cache_key, data)
        return data
    
    def get_vault(self, chain_id: str, vault: str, block_number: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive vault data from the new /vault/{address} endpoint.
        
        Returns all vault data in a single call: vault info, pps, status, config,
        fees, managers, upkeep, and tvl breakdown.
        
        Args:
            chain_id: Blockchain network ID
            vault: SuperVault address
            block_number: Optional block number for historical query
            
        Returns:
            Dict containing comprehensive vault data (VaultDetailsResponse)
        """
        cache_key = f"vault_{chain_id}_{vault}_{block_number or 'latest'}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        endpoint = f"{self.base_url}/api/v1/vault/{vault}"
        params = {"chain_id": chain_id}
        if block_number is not None:
            params["block_number"] = str(block_number)
        
        data = self._request_with_retry(endpoint, params)
        self._store_in_cache(cache_key, data)
        return data
    
    
    def health_check(self) -> bool:
        """Check if the API is healthy.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/health"
            response = self.session.get(endpoint)
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def clear_cache(self) -> None:
        """Clear the shared cache."""
        global _shared_cache
        _shared_cache = {}
    
    def clear_vault_cache(self, chain_id: str, vault: str) -> None:
        """Clear cached data for a specific vault.
        
        Args:
            chain_id: Blockchain network ID
            vault: SuperVault address
        """
        global _shared_cache
        keys_to_remove = [
            f"vault_{chain_id}_{vault}_latest",
            f"pps_{chain_id}_{vault}_latest",
        ]
        for key in keys_to_remove:
            _shared_cache.pop(key, None)
