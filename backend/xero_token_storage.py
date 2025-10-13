"""
Xero Token Storage Module
Handles secure storage and refresh of OAuth tokens
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import base64
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

class XeroTokenManager:
    """
    Manages Xero OAuth tokens with automatic refresh
    """

    def __init__(self, db_path: str = 'xero_tokens.db'):
        """
        Initialize token manager with database

        Args:
            db_path: Path to SQLite database for token storage
        """
        self.db_path = db_path
        self.client_id = os.environ.get('XERO_CLIENT_ID', '')
        self.client_secret = os.environ.get('XERO_CLIENT_SECRET', '')
        self._init_database()

    def _init_database(self):
        """Create database table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS xero_tokens (
                id INTEGER PRIMARY KEY,
                tenant_id TEXT NOT NULL UNIQUE,
                organization_name TEXT,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def store_tokens(self, tenant_id: str, access_token: str, refresh_token: str,
                    expires_in: int, org_name: str = None) -> bool:
        """
        Store or update Xero tokens in database

        Args:
            tenant_id: Xero tenant ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_in: Token expiry in seconds
            org_name: Organization name (optional)

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            expires_at = datetime.now() + timedelta(seconds=expires_in)

            cursor.execute('''
                INSERT OR REPLACE INTO xero_tokens
                (tenant_id, organization_name, access_token, refresh_token, expires_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (tenant_id, org_name, access_token, refresh_token, expires_at))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error storing tokens: {e}")
            return False

    def get_valid_token(self, tenant_id: str) -> Optional[str]:
        """
        Get valid access token, refreshing if necessary

        Args:
            tenant_id: Xero tenant ID

        Returns:
            Valid access token or None if refresh fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT access_token, refresh_token, expires_at, organization_name
                FROM xero_tokens
                WHERE tenant_id = ?
            ''', (tenant_id,))

            result = cursor.fetchone()
            conn.close()

            if not result:
                print(f"No tokens found for tenant: {tenant_id}")
                return None

            access_token, refresh_token, expires_at_str, org_name = result
            expires_at = datetime.fromisoformat(expires_at_str)

            # Check if token is still valid (with 5-minute buffer)
            if datetime.now() < (expires_at - timedelta(minutes=5)):
                return access_token

            # Token expired or expiring soon, refresh it
            print(f"Token expiring soon, refreshing for {org_name}...")
            return self._refresh_token(tenant_id, refresh_token)

        except Exception as e:
            print(f"Error getting token: {e}")
            return None

    def _refresh_token(self, tenant_id: str, refresh_token: str) -> Optional[str]:
        """
        Refresh expired access token

        Args:
            tenant_id: Xero tenant ID
            refresh_token: OAuth refresh token

        Returns:
            New access token or None if refresh fails
        """
        try:
            token_url = 'https://identity.xero.com/connect/token'

            # Prepare refresh request
            token_data = urlencode({
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id
            }).encode('utf-8')

            # Create Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            auth_header = base64.b64encode(credentials.encode()).decode('ascii')

            # Make token request
            token_request = Request(
                token_url,
                data=token_data,
                headers={
                    'Authorization': f'Basic {auth_header}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )

            with urlopen(token_request) as response:
                if response.status == 200:
                    tokens = json.loads(response.read().decode())
                    new_access_token = tokens.get('access_token')
                    new_refresh_token = tokens.get('refresh_token')
                    expires_in = tokens.get('expires_in', 1800)

                    # Update stored tokens
                    if self.store_tokens(tenant_id, new_access_token, new_refresh_token, expires_in):
                        print(f"Successfully refreshed token for tenant: {tenant_id}")
                        return new_access_token

            return None

        except HTTPError as e:
            error_data = e.read().decode() if e.fp else ''
            print(f"Failed to refresh token: {e.code} - {error_data}")
            return None
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    def get_all_tenants(self) -> list:
        """
        Get list of all configured tenants

        Returns:
            List of tenant dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT tenant_id, organization_name, expires_at
                FROM xero_tokens
                ORDER BY updated_at DESC
            ''')

            results = cursor.fetchall()
            conn.close()

            tenants = []
            for tenant_id, org_name, expires_at_str in results:
                expires_at = datetime.fromisoformat(expires_at_str)
                tenants.append({
                    'tenant_id': tenant_id,
                    'organization': org_name,
                    'token_valid': datetime.now() < expires_at,
                    'expires_at': expires_at_str
                })

            return tenants

        except Exception as e:
            print(f"Error getting tenants: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize token manager
    token_manager = XeroTokenManager()

    # Example: Store tokens after successful OAuth
    # token_manager.store_tokens(
    #     tenant_id='0e5c083a-fcab-4f34-a565-3f7af39d8d59',
    #     access_token='your_access_token',
    #     refresh_token='your_refresh_token',
    #     expires_in=1800,
    #     org_name='Liberlocus'
    # )

    # Example: Get valid token (auto-refreshes if needed)
    # token = token_manager.get_valid_token('0e5c083a-fcab-4f34-a565-3f7af39d8d59')

    # List all configured tenants
    tenants = token_manager.get_all_tenants()
    print(f"Configured tenants: {tenants}")