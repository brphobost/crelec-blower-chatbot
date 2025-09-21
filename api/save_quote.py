"""
Save quote data to a persistent storage
For production, consider using a proper database like PostgreSQL or MongoDB
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Save quote data"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length)
            quote_data = json.loads(body_data.decode('utf-8'))

            # Add metadata
            quote_record = {
                'quote_id': quote_data.get('quote_id'),
                'timestamp': datetime.now().isoformat(),
                'customer': {
                    'email': quote_data.get('customer_data', {}).get('email'),
                    'application': quote_data.get('customer_data', {}).get('application'),
                    'tank_dimensions': {
                        'length': quote_data.get('customer_data', {}).get('length'),
                        'width': quote_data.get('customer_data', {}).get('width'),
                        'height': quote_data.get('customer_data', {}).get('height'),
                    },
                    'altitude': quote_data.get('customer_data', {}).get('altitude'),
                },
                'calculation': quote_data.get('calculation', {}),
                'recommended_products': quote_data.get('products', []),
                'session_id': quote_data.get('session_id'),
                'ip_address': self.headers.get('X-Forwarded-For', 'unknown'),
                'user_agent': self.headers.get('User-Agent', 'unknown')
            }

            # For Vercel, we'll use environment variable to store quotes
            # In production, use a proper database
            self.log_quote_to_storage(quote_record)

            # Return success
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'success',
                'message': 'Quote saved successfully',
                'quote_id': quote_data.get('quote_id')
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'status': 'error',
                'message': str(e)
            }

            self.wfile.write(json.dumps(error_response).encode())

    def log_quote_to_storage(self, quote_record):
        """
        Save quote to storage
        For demo: prints to Vercel logs
        For production: integrate with database
        """
        # Log to Vercel console (visible in Vercel dashboard)
        print(f"QUOTE_GENERATED: {json.dumps(quote_record)}")

        # You could also send to external services:
        # - Google Sheets API
        # - Airtable
        # - PostgreSQL
        # - MongoDB
        # - Firebase

        # Example: Save to a quotes.json file locally (not persistent on Vercel)
        try:
            quotes_file = '/tmp/quotes.json'

            # Read existing quotes
            try:
                with open(quotes_file, 'r') as f:
                    quotes = json.load(f)
            except:
                quotes = []

            # Add new quote
            quotes.append(quote_record)

            # Save back
            with open(quotes_file, 'w') as f:
                json.dump(quotes, f, indent=2)

        except Exception as e:
            print(f"Error saving to file: {e}")


# For local testing
if __name__ == "__main__":
    print("""
    Quote Storage Options:

    1. Vercel KV Storage (Recommended)
       - Built-in Redis database
       - 30MB free tier
       - Persistent across deployments

    2. Google Sheets
       - Free and easy to set up
       - Good for small volumes
       - Easy to share with client

    3. Airtable
       - Better than Sheets for structured data
       - Free tier available
       - Good API and UI

    4. Supabase/PostgreSQL
       - Professional database
       - Free tier available
       - Best for scaling
    """)