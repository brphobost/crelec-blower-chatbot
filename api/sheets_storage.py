"""
Google Sheets storage for quotes
Simple solution that Crelec can access easily
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from datetime import datetime
import os

# Google Sheets Web App URL (from Apps Script)
SHEETS_WEBHOOK_URL = os.getenv('SHEETS_WEBHOOK_URL', '')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Save quote to Google Sheets"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length)
            quote_data = json.loads(body_data.decode('utf-8'))

            # Format for Google Sheets
            sheet_row = {
                'timestamp': datetime.now().isoformat(),
                'quote_id': quote_data.get('quote_id'),
                'email': quote_data.get('customer_data', {}).get('email'),
                'application': quote_data.get('customer_data', {}).get('application'),
                'tank_length': quote_data.get('customer_data', {}).get('length'),
                'tank_width': quote_data.get('customer_data', {}).get('width'),
                'tank_height': quote_data.get('customer_data', {}).get('height'),
                'tank_volume': quote_data.get('calculation', {}).get('tank_volume'),
                'altitude': quote_data.get('customer_data', {}).get('altitude'),
                'airflow_required': quote_data.get('calculation', {}).get('airflow_required'),
                'pressure_required': quote_data.get('calculation', {}).get('pressure_required'),
                'power_estimate': quote_data.get('calculation', {}).get('power_estimate'),
                'products_recommended': len(quote_data.get('products', [])),
                'product_1': quote_data.get('products', [{}])[0].get('model', ''),
                'product_1_price': quote_data.get('products', [{}])[0].get('price', ''),
                'session_id': quote_data.get('session_id'),
            }

            # Send to Google Sheets if webhook URL is configured
            if SHEETS_WEBHOOK_URL:
                self.send_to_sheets(sheet_row)

            # Log to console for Vercel logs
            print(f"QUOTE_LOGGED: {json.dumps(sheet_row)}")

            # Return success
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'success',
                'message': 'Quote logged successfully',
                'quote_id': quote_data.get('quote_id')
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Error logging quote: {e}")
            self.send_response(200)  # Still return 200 to not break the flow
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'logged_with_error',
                'message': str(e)
            }

            self.wfile.write(json.dumps(response).encode())

    def send_to_sheets(self, data):
        """Send data to Google Sheets via Apps Script Web App"""
        try:
            req = urllib.request.Request(
                SHEETS_WEBHOOK_URL,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            print("Sent to Google Sheets successfully")
        except Exception as e:
            print(f"Failed to send to Sheets: {e}")


"""
GOOGLE SHEETS SETUP INSTRUCTIONS:

1. Create a Google Sheet with these columns:
   A: Timestamp
   B: Quote ID
   C: Email
   D: Application
   E: Tank Length
   F: Tank Width
   G: Tank Height
   H: Tank Volume
   I: Altitude
   J: Airflow Required
   K: Pressure Required
   L: Power Estimate
   M: Products Recommended
   N: Product 1
   O: Product 1 Price
   P: Session ID

2. Go to Extensions > Apps Script

3. Paste this code:

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    data.timestamp,
    data.quote_id,
    data.email,
    data.application,
    data.tank_length,
    data.tank_width,
    data.tank_height,
    data.tank_volume,
    data.altitude,
    data.airflow_required,
    data.pressure_required,
    data.power_estimate,
    data.products_recommended,
    data.product_1,
    data.product_1_price,
    data.session_id
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({status: 'success'}))
    .setMimeType(ContentService.MimeType.JSON);
}

4. Deploy > New Deployment
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone

5. Copy the Web App URL

6. Add to Vercel Environment Variables:
   SHEETS_WEBHOOK_URL = your-web-app-url

That's it! All quotes will be logged to your Google Sheet.
"""