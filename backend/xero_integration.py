"""
Xero Inventory Integration Module for Crelec Blower Chatbot
Syncs product inventory data from Xero accounting system
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from urllib.parse import urlencode
import base64
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XeroInventorySync:
    """
    Handles synchronization of inventory data from Xero to local product catalog
    """

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize Xero integration with credentials

        Args:
            client_id: Xero OAuth2 client ID
            client_secret: Xero OAuth2 client secret
        """
        self.client_id = client_id or os.getenv('XERO_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('XERO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('XERO_REDIRECT_URI', 'http://localhost:8000/callback')

        # API endpoints
        self.authorize_url = 'https://login.xero.com/identity/connect/authorize'
        self.token_url = 'https://identity.xero.com/connect/token'
        self.api_base = 'https://api.xero.com/api.xro/2.0'
        self.connections_url = 'https://api.xero.com/connections'

        # Token storage (in production, use secure storage)
        self.access_token = None
        self.refresh_token = None
        self.tenant_id = None
        self.token_expires = None

    def generate_oauth_url(self, state: str = None, scope: str = 'accounting.transactions.read') -> str:
        """
        Generate OAuth2 authorization URL for user to authorize Xero access

        Args:
            state: Optional state parameter for security
            scope: OAuth scopes needed (default: read accounting transactions)

        Returns:
            Authorization URL for user to visit
        """
        if not state:
            state = secrets.token_urlsafe(32)

        # Generate PKCE challenge (recommended for security)
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        auth_url = f"{self.authorize_url}?{urlencode(params)}"

        # Store code_verifier for token exchange
        self.code_verifier = code_verifier

        return auth_url

    def exchange_code_for_token(self, code: str) -> bool:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'code_verifier': getattr(self, 'code_verifier', '')
            }

            response = requests.post(
                self.token_url,
                data=data,
                auth=(self.client_id, self.client_secret)
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'])

                # Get tenant ID
                self._get_tenant_id()

                logger.info("Successfully obtained Xero access token")
                return True
            else:
                logger.error(f"Failed to exchange code: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False

    def refresh_access_token(self) -> bool:
        """
        Refresh expired access token using refresh token

        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False

        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id
            }

            response = requests.post(
                self.token_url,
                data=data,
                auth=(self.client_id, self.client_secret)
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'])

                logger.info("Successfully refreshed Xero access token")
                return True
            else:
                logger.error(f"Failed to refresh token: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False

    def _get_tenant_id(self) -> bool:
        """
        Get tenant ID for authorized Xero organization

        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(self.connections_url, headers=headers)

            if response.status_code == 200:
                connections = response.json()
                if connections:
                    self.tenant_id = connections[0]['tenantId']
                    logger.info(f"Got tenant ID: {self.tenant_id}")
                    return True

            logger.error(f"Failed to get tenant ID: {response.text}")
            return False

        except Exception as e:
            logger.error(f"Error getting tenant ID: {e}")
            return False

    def fetch_inventory_items(self, only_tracked: bool = True) -> Optional[List[Dict]]:
        """
        Fetch all inventory items from Xero

        Args:
            only_tracked: If True, only fetch tracked inventory items

        Returns:
            List of inventory items or None if error
        """
        # Check token expiry and refresh if needed
        if self.token_expires and datetime.now() >= self.token_expires:
            if not self.refresh_access_token():
                return None

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Xero-tenant-id': self.tenant_id,
                'Accept': 'application/json'
            }

            params = {}
            if only_tracked:
                params['where'] = 'IsTrackedAsInventory==true'

            response = requests.get(
                f"{self.api_base}/Items",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                logger.info(f"Fetched {len(items)} inventory items from Xero")
                return items
            else:
                logger.error(f"Failed to fetch inventory: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error fetching inventory: {e}")
            return None

    def map_xero_to_blower_product(self, xero_item: Dict) -> Dict:
        """
        Map Xero inventory item to blower product format

        Args:
            xero_item: Item data from Xero API

        Returns:
            Product dictionary in chatbot format
        """
        # Extract specifications from description or name
        # This mapping will need to be customized based on actual Xero data structure

        product = {
            'model': xero_item.get('Code', ''),
            'name': xero_item.get('Name', ''),
            'description': xero_item.get('Description', ''),
            'price': 0,
            'stock_level': 0,
            'in_stock': False,
            'specifications': {}
        }

        # Get price from sales details
        if 'SalesDetails' in xero_item:
            product['price'] = float(xero_item['SalesDetails'].get('UnitPrice', 0))

        # Get stock level if tracked
        if xero_item.get('IsTrackedAsInventory'):
            product['stock_level'] = int(xero_item.get('QuantityOnHand', 0))
            product['in_stock'] = product['stock_level'] > 0

        # Try to extract specifications from description
        # Format expected: "Airflow: 720m³/hr, Pressure: 300mbar, Power: 5.5kW"
        description = xero_item.get('Description', '')
        if description:
            specs = self._parse_specifications(description)
            product['specifications'] = specs

        return product

    def _parse_specifications(self, description: str) -> Dict:
        """
        Parse blower specifications from description text

        Args:
            description: Product description containing specs

        Returns:
            Dictionary of specifications
        """
        specs = {
            'airflow_m3_min': None,
            'airflow_m3_hr': None,
            'pressure_mbar': None,
            'power_kw': None
        }

        # Common patterns in descriptions
        # Examples: "720m³/hr", "12m³/min", "300mbar", "5.5kW"
        import re

        # Airflow in m³/hr
        airflow_hr = re.search(r'(\d+(?:\.\d+)?)\s*m[³3]/hr', description, re.IGNORECASE)
        if airflow_hr:
            specs['airflow_m3_hr'] = float(airflow_hr.group(1))
            specs['airflow_m3_min'] = specs['airflow_m3_hr'] / 60

        # Airflow in m³/min
        airflow_min = re.search(r'(\d+(?:\.\d+)?)\s*m[³3]/min', description, re.IGNORECASE)
        if airflow_min:
            specs['airflow_m3_min'] = float(airflow_min.group(1))
            specs['airflow_m3_hr'] = specs['airflow_m3_min'] * 60

        # Pressure in mbar
        pressure = re.search(r'(\d+(?:\.\d+)?)\s*mbar', description, re.IGNORECASE)
        if pressure:
            specs['pressure_mbar'] = float(pressure.group(1))

        # Power in kW
        power = re.search(r'(\d+(?:\.\d+)?)\s*kW', description, re.IGNORECASE)
        if power:
            specs['power_kw'] = float(power.group(1))

        return specs

    def sync_to_product_catalog(self, output_file: str = 'products_from_xero.json') -> bool:
        """
        Sync Xero inventory to local product catalog JSON file

        Args:
            output_file: Path to output JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch items from Xero
            xero_items = self.fetch_inventory_items()

            if not xero_items:
                logger.warning("No items fetched from Xero")
                return False

            # Convert to blower product format
            products = []
            for item in xero_items:
                # Filter for blower products (customize based on actual data)
                # For example, only items with certain codes or categories
                if self._is_blower_product(item):
                    product = self.map_xero_to_blower_product(item)
                    products.append(product)

            # Save to JSON file
            with open(output_file, 'w') as f:
                json.dump(products, f, indent=2)

            logger.info(f"Successfully synced {len(products)} products to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error syncing to product catalog: {e}")
            return False

    def _is_blower_product(self, xero_item: Dict) -> bool:
        """
        Check if Xero item is a blower product

        Args:
            xero_item: Item from Xero API

        Returns:
            True if item is a blower product
        """
        # Customize this based on how blowers are identified in Xero
        # Examples:
        # - Check if code starts with certain prefix
        # - Check if name contains "blower"
        # - Check if in specific category

        name = xero_item.get('Name', '').lower()
        code = xero_item.get('Code', '').lower()

        # Basic checks - customize based on actual data
        blower_keywords = ['blower', 'ghbh', 'sirocco', 'goorui']

        for keyword in blower_keywords:
            if keyword in name or keyword in code:
                return True

        return False

    def get_single_product(self, product_code: str) -> Optional[Dict]:
        """
        Get single product details from Xero by product code

        Args:
            product_code: Product code/SKU to search for

        Returns:
            Product dictionary or None if not found
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Xero-tenant-id': self.tenant_id,
                'Accept': 'application/json'
            }

            # Search by code
            params = {
                'where': f'Code=="{product_code}"'
            }

            response = requests.get(
                f"{self.api_base}/Items",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])

                if items:
                    return self.map_xero_to_blower_product(items[0])

            return None

        except Exception as e:
            logger.error(f"Error fetching single product: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Initialize with credentials (in production, use environment variables)
    xero = XeroInventorySync()

    # Step 1: Generate OAuth URL for user authorization
    auth_url = xero.generate_oauth_url()
    print(f"Please visit this URL to authorize Xero access:\n{auth_url}")

    # Step 2: After user authorizes, they'll be redirected with a code
    # In production, this would be handled by your callback endpoint
    # auth_code = input("Enter the authorization code from callback: ")
    # xero.exchange_code_for_token(auth_code)

    # Step 3: Fetch and sync inventory (after authorization)
    # xero.sync_to_product_catalog()

    print("\nXero integration module ready for use!")
    print("Next steps:")
    print("1. Set up environment variables (XERO_CLIENT_ID, XERO_CLIENT_SECRET)")
    print("2. Register app at developer.xero.com")
    print("3. Implement OAuth callback endpoint")
    print("4. Schedule regular sync jobs")