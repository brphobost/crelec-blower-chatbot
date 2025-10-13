"""
Test endpoint to fetch inventory from Xero
This will help verify the integration is working
"""

import json
import os
import base64
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Test fetching inventory items from Xero
        For demo purposes - in production, use stored tokens
        """
        try:
            # For testing, we'll need to get a fresh token
            # In production, you'd use stored refresh tokens

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            html_response = """
            <html>
            <head>
                <title>Xero Inventory Test</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    h1 { color: #333; }
                    .info-box {
                        background: #e3f2fd;
                        border-left: 4px solid #2196f3;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }
                    .warning-box {
                        background: #fff3cd;
                        border-left: 4px solid #ff9800;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }
                    .item-card {
                        background: white;
                        border: 1px solid #ddd;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .item-header {
                        font-weight: bold;
                        color: #1976d2;
                        margin-bottom: 10px;
                    }
                    .item-detail {
                        margin: 5px 0;
                        color: #666;
                    }
                    .stock-badge {
                        display: inline-block;
                        padding: 3px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    .in-stock {
                        background: #c8e6c9;
                        color: #2e7d32;
                    }
                    .out-of-stock {
                        background: #ffcdd2;
                        color: #c62828;
                    }
                    button {
                        background: #2196f3;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        margin: 10px 5px;
                    }
                    button:hover {
                        background: #1976d2;
                    }
                </style>
            </head>
            <body>
                <h1>🔍 Xero Inventory Test</h1>

                <div class="warning-box">
                    <strong>⚠️ Note:</strong> This is a test page. To fetch inventory, you need to:
                    <ol>
                        <li>First authorize via the admin panel</li>
                        <li>Store the access/refresh tokens</li>
                        <li>Use those tokens to fetch inventory</li>
                    </ol>
                </div>

                <div class="info-box">
                    <h3>How to Test Inventory Fetch:</h3>
                    <p>Since we just connected to Xero, the access token is temporary (30 minutes).</p>
                    <p>In production, you would:</p>
                    <ul>
                        <li>Store the refresh token in a database</li>
                        <li>Use it to get new access tokens automatically</li>
                        <li>Fetch inventory items using the Xero API</li>
                        <li>Map Xero items to your blower products</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h3>Sample Xero API Call (What would happen):</h3>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">
GET https://api.xero.com/api.xro/2.0/Items
Headers:
  Authorization: Bearer [access_token]
  Xero-tenant-id: 0e5c083a-fcab-4f34-a565-3f7af39d8d59
  Accept: application/json

Response would include:
{
  "Items": [
    {
      "ItemID": "...",
      "Code": "GHBH-2D-720",
      "Name": "Goorui Blower 720m³/hr",
      "Description": "Side channel blower, 720m³/hr, 300mbar, 5.5kW",
      "QuantityOnHand": 5,
      "SalesDetails": {
        "UnitPrice": 15000.00
      }
    }
  ]
}</pre>
                </div>

                <h2>Next Steps:</h2>
                <div style="margin: 20px 0;">
                    <button onclick="window.location.href='/xero-admin.html'">Back to Admin Panel</button>
                    <button onclick="window.location.href='/'">Back to Chatbot</button>
                </div>

                <div class="warning-box">
                    <strong>To Complete Integration:</strong>
                    <ol>
                        <li>Set up a database to store tokens</li>
                        <li>Create a scheduled job to refresh tokens before expiry</li>
                        <li>Implement inventory sync that runs every 15 minutes</li>
                        <li>Map Xero products to your blower catalog</li>
                    </ol>
                </div>
            </body>
            </html>
            """

            self.wfile.write(html_response.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
            <html>
                <body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #dc3545;">Error</h1>
                    <p>{str(e)}</p>
                    <a href="/xero-admin.html">Back to Admin</a>
                </body>
            </html>
            """.encode())