"""
Google Sheets Product Catalog Integration
Fetches live product data from Google Sheets
Allows customer to maintain products without code changes
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Fetch products from Google Sheets"""
        try:
            # Google Sheets configuration
            # Customer's live Google Sheet
            SHEET_ID = "14x7T9cHol94jk3w4CgZggKIYrYSMpefRrflYfC0HUk4"
            SHEET_NAME = "Sheet1"  # Default tab name
            API_KEY = ""  # Not needed for public sheets

            # Build Google Sheets API URL
            # Using CSV export for simplicity (no API key needed if sheet is public)
            csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={SHEET_NAME}"

            # For private sheets with API key:
            # range = f"{SHEET_NAME}!A1:Z1000"
            # api_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range}?key={API_KEY}"

            # Fetch data
            with urllib.request.urlopen(csv_url) as response:
                raw_data = response.read().decode('utf-8')

            # Parse Google Visualization API response
            # Remove the JavaScript wrapper to get JSON
            json_str = raw_data.split('(', 1)[1].rsplit(')', 1)[0]
            data = json.loads(json_str)

            # Convert to our product format
            products = []
            rows = data['table']['rows']

            # Skip header row, process data rows
            for row in rows[1:]:  # Assuming first row is headers
                try:
                    cells = row['c']
                    # Match simplified format: Model, Airflow, Pressure, Power, In Stock
                    product = {
                        'model': cells[0]['v'] if cells[0] else '',
                        'airflow_m3_min': float(cells[1]['v']) if cells[1] else 0,
                        'airflow': float(cells[1]['v']) * 60 if cells[1] else 0,  # Convert to m³/hr
                        'pressure': float(cells[2]['v']) if cells[2] else 0,
                        'power': float(cells[3]['v']) if cells[3] else 0,
                        'in_stock': str(cells[4]['v']).lower() == 'yes' if cells[4] else False
                    }

                    # Only add if essential fields are present
                    if product['model'] and product['airflow'] > 0:
                        products.append(product)

                except (IndexError, KeyError, ValueError, TypeError):
                    continue  # Skip malformed rows

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response_data = {
                'products': products,
                'count': len(products),
                'source': 'google_sheets',
                'sheet_id': SHEET_ID
            }

            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            # Fallback to local products.json if Sheets unavailable
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'error': str(e),
                'fallback': 'Use local products.json'
            }

            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()