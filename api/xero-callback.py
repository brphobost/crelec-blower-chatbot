"""
Xero OAuth Callback Handler for Vercel
Handles the OAuth 2.0 callback from Xero after user authorization
"""

import json
import os
import base64
from urllib.parse import parse_qs, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle OAuth callback from Xero
        Receives authorization code and exchanges it for access token
        """
        try:
            # Parse query parameters
            query_string = self.path.split('?')[1] if '?' in self.path else ''
            params = parse_qs(query_string)

            # Get authorization code from callback
            code = params.get('code', [None])[0]
            state = params.get('state', [None])[0]
            error = params.get('error', [None])[0]

            # Check for errors
            if error:
                error_desc = params.get('error_description', ['Unknown error'])[0]
                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                <html>
                    <head><title>Xero Authorization Failed</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                        <h1 style="color: #dc3545;">Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p>Description: {error_desc}</p>
                        <a href="/">Return to Chatbot</a>
                    </body>
                </html>
                """.encode())
                return

            if not code:
                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                    <head><title>Missing Authorization Code</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                        <h1 style="color: #dc3545;">Missing Authorization Code</h1>
                        <p>No authorization code received from Xero.</p>
                        <a href="/">Return to Chatbot</a>
                    </body>
                </html>
                """)
                return

            # Exchange code for token
            token_url = 'https://identity.xero.com/connect/token'

            # Get credentials from environment variables
            client_id = os.environ.get('XERO_CLIENT_ID', '').strip()
            client_secret = os.environ.get('XERO_CLIENT_SECRET', '').strip()
            redirect_uri = 'https://blower-chatbot.vercel.app/api/xero-callback'

            # Debug logging (remove in production)
            print(f"Client ID present: {bool(client_id)}")
            print(f"Client Secret present: {bool(client_secret)}")
            print(f"Redirect URI: {redirect_uri}")

            # Prepare token request
            token_data = urlencode({
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id  # Some OAuth providers need this in the body too
            }).encode('utf-8')

            # Create Basic Auth header
            credentials = f"{client_id}:{client_secret}"
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

            try:
                with urlopen(token_request) as response:
                    if response.status == 200:
                        # Success - got tokens
                        tokens = json.loads(response.read().decode())
                        access_token = tokens.get('access_token')
                        refresh_token = tokens.get('refresh_token')
                        expires_in = tokens.get('expires_in', 1800)

                        # Get tenant ID
                        connections_request = Request(
                            'https://api.xero.com/connections',
                            headers={'Authorization': f'Bearer {access_token}'}
                        )

                        tenant_id = None
                        org_name = None

                        try:
                            with urlopen(connections_request) as conn_response:
                                if conn_response.status == 200:
                                    connections = json.loads(conn_response.read().decode())
                                    if connections:
                                        tenant_id = connections[0].get('tenantId')
                                        org_name = connections[0].get('tenantName', 'Unknown')
                        except Exception as e:
                            # Continue even if we can't get tenant info
                            print(f"Could not get tenant info: {e}")

                        # Store tokens securely (in production, use database or secure storage)
                        # For now, we'll display success message

                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(f"""
                        <html>
                            <head>
                                <title>Xero Authorization Successful</title>
                                <style>
                                    body {{
                                        font-family: Arial, sans-serif;
                                        padding: 40px;
                                        max-width: 600px;
                                        margin: 0 auto;
                                        background-color: #f8f9fa;
                                    }}
                                    .success-box {{
                                        background: white;
                                        border-radius: 8px;
                                        padding: 30px;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    }}
                                    h1 {{ color: #28a745; }}
                                    .info-box {{
                                        background: #e7f3ff;
                                        border-left: 4px solid #0078d4;
                                        padding: 15px;
                                        margin: 20px 0;
                                    }}
                                    button {{
                                        background: #0078d4;
                                        color: white;
                                        padding: 10px 20px;
                                        border: none;
                                        border-radius: 4px;
                                        cursor: pointer;
                                        margin-top: 20px;
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="success-box">
                                    <h1>✅ Xero Authorization Successful!</h1>
                                    <p>Successfully connected to Xero organization: <strong>{org_name or 'Unknown'}</strong></p>

                                    <div class="info-box">
                                        <h3>Connection Details:</h3>
                                        <p><strong>Tenant ID:</strong> {tenant_id or 'Not retrieved'}</p>
                                        <p><strong>Token expires in:</strong> {expires_in // 60} minutes</p>
                                    </div>

                                    <div class="info-box">
                                        <h3>Next Steps:</h3>
                                        <ol>
                                            <li>Tokens have been generated successfully</li>
                                            <li>Configure automatic token storage in your database</li>
                                            <li>Set up scheduled inventory sync jobs</li>
                                            <li>Test product fetching from Xero</li>
                                        </ol>
                                    </div>

                                    <p><strong>Important:</strong> In production, these tokens should be securely stored in a database, not displayed.</p>

                                    <button onclick="window.location.href='/'">Return to Chatbot</button>
                                </div>
                            </body>
                        </html>
                        """.encode())

                        # Log successful connection
                        print(f"Successfully connected to Xero org: {org_name}, Tenant: {tenant_id}")

            except HTTPError as e:
                # Token exchange failed
                error_data = e.read().decode() if e.fp else ''

                # Parse error if it's JSON
                try:
                    error_json = json.loads(error_data)
                    error_message = error_json.get('error', 'Unknown error')
                    error_desc = error_json.get('error_description', '')
                except:
                    error_message = error_data
                    error_desc = ''

                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                <html>
                    <head><title>Token Exchange Failed</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #dc3545;">Token Exchange Failed</h1>
                        <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>Error:</strong> {error_message}</p>
                            {"<p><strong>Description:</strong> " + error_desc + "</p>" if error_desc else ""}
                            <p><strong>Status Code:</strong> {e.code}</p>
                        </div>

                        <div style="background: #fff3cd; border: 1px solid #ffecd1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3>Troubleshooting:</h3>
                            <ul style="text-align: left;">
                                <li>Verify the redirect URI in Xero matches: <code>https://blower-chatbot.vercel.app/api/xero-callback</code></li>
                                <li>Check that Client ID and Secret are correctly set in Vercel environment variables</li>
                                <li>Ensure the Xero app is not in demo mode</li>
                                <li>Try regenerating the Client Secret in Xero if needed</li>
                            </ul>
                        </div>

                        <a href="/xero-admin.html" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Back to Admin Panel</a>
                    </body>
                </html>
                """.encode())

        except Exception as e:
            # Handle any other errors
            self.send_response(500)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
            <html>
                <head><title>Server Error</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1 style="color: #dc3545;">Server Error</h1>
                    <p>An error occurred processing the callback: {str(e)}</p>
                    <a href="/">Return to Chatbot</a>
                </body>
            </html>
            """.encode())