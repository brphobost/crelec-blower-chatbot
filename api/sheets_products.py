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
            # Sheet must be publicly readable or use API key
            SHEET_ID = "YOUR_GOOGLE_SHEET_ID"  # e.g., "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            SHEET_NAME = "Products"  # Name of the sheet tab
            API_KEY = "YOUR_GOOGLE_API_KEY"  # Optional: for private sheets

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
                    product = {
                        'id': cells[0]['v'] if cells[0] else '',
                        'model': cells[1]['v'] if cells[1] else '',
                        'brand': cells[2]['v'] if cells[2] else '',
                        'airflow_min': float(cells[3]['v']) if cells[3] else 0,
                        'airflow_max': float(cells[4]['v']) if cells[4] else 0,
                        'pressure_min': float(cells[5]['v']) if cells[5] else 0,
                        'pressure_max': float(cells[6]['v']) if cells[6] else 0,
                        'power': float(cells[7]['v']) if cells[7] else 0,
                        'price': float(cells[8]['v']) if cells[8] else 0,
                        'currency': cells[9]['v'] if cells[9] else 'ZAR',
                        'stock_status': cells[10]['v'] if cells[10] else 'check',
                        'delivery_days': int(cells[11]['v']) if cells[11] else 0,
                        'description': cells[12]['v'] if cells[12] else '',
                        'warranty_years': int(cells[13]['v']) if cells[13] else 1,
                        'efficiency_rating': cells[14]['v'] if cells[14] else '',
                        'noise_level': cells[15]['v'] if cells[15] else '',
                        'last_updated': cells[16]['v'] if cells[16] else ''
                    }

                    # Only add if essential fields are present
                    if product['model'] and product['airflow_max'] > 0:
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