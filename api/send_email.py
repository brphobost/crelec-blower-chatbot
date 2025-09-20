"""
Resend.com email service - Works immediately without domain verification
Perfect for testing and demo purposes
"""

from http.server import BaseHTTPRequestHandler
import json
import base64
import os
from datetime import datetime, timedelta
import urllib.request

# Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_YOUR_KEY_HERE')  # Get from resend.com
FROM_EMAIL = "onboarding@resend.dev"  # Resend's test email (works immediately!)
FROM_NAME = "Crelec Blower System"
ADMIN_EMAIL = "brkorkut@yahoo.com"  # Temporary for testing - change to crelec@live.co.za for production

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST request to send email"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length)
            data = json.loads(body_data.decode('utf-8'))

            # Extract email data
            to_email = data.get('to_email')
            quote_id = data.get('quote_id')
            customer_data = data.get('customer_data', {})
            calculation = data.get('calculation', {})
            products = data.get('products', [])
            pdf_base64 = data.get('pdf_attachment', '')

            # Build Resend API request
            email_data = {
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": [to_email],
                "cc": [ADMIN_EMAIL],
                "reply_to": ADMIN_EMAIL,
                "subject": f"Crelec Blower Quote #{quote_id}",
                "html": self.generate_html_email(quote_id, calculation, products, customer_data),
                "text": self.generate_plain_email(quote_id, calculation, products, customer_data)
            }

            # Add PDF attachment if provided
            if pdf_base64:
                email_data["attachments"] = [
                    {
                        "content": pdf_base64,
                        "filename": f"Crelec_Quote_{quote_id}.pdf"
                    }
                ]

            # Send via Resend API
            try:
                req = urllib.request.Request(
                    'https://api.resend.com/emails',
                    data=json.dumps(email_data).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {RESEND_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                )

                response = urllib.request.urlopen(req)
                response_data = json.loads(response.read().decode('utf-8'))

                email_sent = True
                message = f'Quote emailed successfully to {to_email}'

            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"Resend error: {e.code} - {error_body}")

                if e.code == 401:
                    email_sent = False
                    message = 'Email service not configured. Please add RESEND_API_KEY. PDF downloaded successfully.'
                else:
                    email_sent = False
                    message = f'Email sending failed. PDF downloaded successfully.'

            except Exception as email_error:
                print(f"Email error: {email_error}")
                email_sent = False
                message = 'Email service temporarily unavailable. PDF downloaded successfully.'

            # Return response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'success' if email_sent else 'partial',
                'message': message,
                'quote_id': quote_id,
                'email_sent': email_sent
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

    def generate_html_email(self, quote_id, calculation, products, customer_data):
        """Generate HTML email content"""
        valid_until = (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background: #1a3e4c; color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">CRELEC S.A.</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px;">SIDE CHANNEL BLOWERS & VACUUM PUMPS</p>
                </div>

                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #1a3e4c; margin-top: 0;">Your Blower Quote is Ready!</h2>

                    <p>Dear Customer,</p>

                    <p><em style="color: #666;">Note: This is a demo system set up by Liberlocus for Crelec S.A.</em></p>

                    <p>Thank you for using our Blower Selection Assistant. Based on your requirements, we've prepared a customized quote with our recommended products.</p>

                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                        <h3 style="color: #1a3e4c; margin-top: 0;">Quote Information</h3>
                        <p><strong>Quote ID:</strong> {quote_id}<br>
                        <strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}<br>
                        <strong>Valid Until:</strong> {valid_until}</p>
                    </div>

                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                        <h3 style="color: #0066cc; margin-top: 0;">Your Requirements</h3>
                        <p>
                        <strong>Tank Volume:</strong> {calculation.get('tank_volume', 'N/A')} m³<br>
                        <strong>Required Airflow:</strong> {calculation.get('airflow_required', 'N/A')} m³/hr<br>
                        <strong>Required Pressure:</strong> {calculation.get('pressure_required', 'N/A')} mbar<br>
                        <strong>Estimated Power:</strong> {calculation.get('power_estimate', 'N/A')} kW
                        </p>
                    </div>

                    <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #2e7d32; margin-top: 0;">✓ We Found {len(products)} Matching Products</h3>
                        <p>Please review the attached PDF for complete details.</p>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <p><strong>Contact Crelec:</strong><br>
                        Email: crelec@live.co.za<br>
                        Phone: +27 11 444 4555</p>
                    </div>

                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <div style="text-align: center; color: #666; font-size: 12px;">
                        <p>Demo system powered by Liberlocus</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    def generate_plain_email(self, quote_id, calculation, products, customer_data):
        """Generate plain text email content"""
        valid_until = (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')

        return f"""
CRELEC S.A. - BLOWER SELECTION QUOTE

Note: This is a demo system set up by Liberlocus for Crelec S.A.

Dear Customer,

Thank you for using our Blower Selection Assistant.

QUOTE INFORMATION
-----------------
Quote ID: {quote_id}
Date: {datetime.now().strftime('%B %d, %Y')}
Valid Until: {valid_until}

YOUR REQUIREMENTS
-----------------
Tank Volume: {calculation.get('tank_volume', 'N/A')} m³
Required Airflow: {calculation.get('airflow_required', 'N/A')} m³/hr
Required Pressure: {calculation.get('pressure_required', 'N/A')} mbar
Estimated Power: {calculation.get('power_estimate', 'N/A')} kW

We found {len(products)} products that match your requirements.
Please see the attached PDF for complete details.

Contact Crelec:
Email: crelec@live.co.za
Phone: +27 11 444 4555

--
Demo system powered by Liberlocus
        """


if __name__ == "__main__":
    print("""
    ========================================
    RESEND SETUP (WORKS IMMEDIATELY):
    ========================================

    1. Sign up at: https://resend.com
       (Free: 100 emails/day, NO domain verification needed!)

    2. Get your API Key:
       - Dashboard shows API key immediately
       - Copy it (starts with 're_')

    3. Add to Vercel:
       - Environment Variables
       - Add: RESEND_API_KEY = your-key
       - Redeploy

    BENEFITS:
    - Works immediately without domain verification
    - Uses resend.dev email for testing
    - Perfect for demos and testing
    - Can upgrade to custom domain later

    ========================================
    """)