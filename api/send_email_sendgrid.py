"""
SendGrid email service for Crelec Blower Chatbot
Professional email sending without Gmail account
"""

from http.server import BaseHTTPRequestHandler
import json
import base64
import os
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

# Configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', 'SG.YOUR_API_KEY_HERE')  # Add your SendGrid API key
FROM_EMAIL = "noreply@crelec.co.za"  # Can use any email with SendGrid
FROM_NAME = "Crelec S.A."
ADMIN_EMAIL = "crelec@live.co.za"

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

            # Build SendGrid API request
            email_data = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "cc": [{"email": ADMIN_EMAIL}],
                        "subject": f"Crelec Blower Quote #{quote_id}"
                    }
                ],
                "from": {
                    "email": FROM_EMAIL,
                    "name": FROM_NAME
                },
                "content": [
                    {
                        "type": "text/html",
                        "value": self.generate_html_email(quote_id, calculation, products, customer_data)
                    },
                    {
                        "type": "text/plain",
                        "value": self.generate_plain_email(quote_id, calculation, products, customer_data)
                    }
                ]
            }

            # Add PDF attachment if provided
            if pdf_base64:
                email_data["attachments"] = [
                    {
                        "content": pdf_base64,
                        "filename": f"Crelec_Quote_{quote_id}.pdf",
                        "type": "application/pdf",
                        "disposition": "attachment"
                    }
                ]

            # Send via SendGrid API
            try:
                req = urllib.request.Request(
                    'https://api.sendgrid.com/v3/mail/send',
                    data=json.dumps(email_data).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {SENDGRID_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                )

                response = urllib.request.urlopen(req)
                email_sent = response.status == 202
                message = f'Quote emailed successfully to {to_email}'

            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"SendGrid error: {e.code} - {error_body}")

                # Check if it's an API key issue
                if e.code == 401:
                    email_sent = False
                    message = 'Email service not configured. Please set up SendGrid API key. PDF downloaded successfully.'
                else:
                    email_sent = False
                    message = f'Email sending failed. PDF downloaded successfully. Error: {e.code}'

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
            # Error response
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
                <!-- Header -->
                <div style="background: #1a3e4c; color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">CRELEC S.A.</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px;">SIDE CHANNEL BLOWERS & VACUUM PUMPS</p>
                </div>

                <!-- Content -->
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #1a3e4c; margin-top: 0;">Your Blower Quote is Ready!</h2>

                    <p>Dear Customer,</p>

                    <p>Thank you for using our Blower Selection Assistant. Based on your requirements, we've prepared a customized quote with our recommended products.</p>

                    <!-- Quote Details Box -->
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                        <h3 style="color: #1a3e4c; margin-top: 0; border-bottom: 2px solid #1a3e4c; padding-bottom: 10px;">Quote Information</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0;"><strong>Quote Number:</strong></td>
                                <td style="padding: 8px 0; color: #0066cc;">{quote_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Date:</strong></td>
                                <td style="padding: 8px 0;">{datetime.now().strftime('%B %d, %Y')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Valid Until:</strong></td>
                                <td style="padding: 8px 0;">{valid_until}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Application:</strong></td>
                                <td style="padding: 8px 0;">{customer_data.get('application', 'Industrial')}</td>
                            </tr>
                        </table>
                    </div>

                    <!-- Requirements Box -->
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                        <h3 style="color: #0066cc; margin-top: 0; border-bottom: 2px solid #0066cc; padding-bottom: 10px;">Your Requirements</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0;"><strong>Tank Volume:</strong></td>
                                <td style="padding: 8px 0;">{calculation.get('tank_volume', 'N/A')} m³</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Required Airflow:</strong></td>
                                <td style="padding: 8px 0; color: #0066cc; font-weight: bold;">{calculation.get('airflow_required', 'N/A')} m³/hr</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Required Pressure:</strong></td>
                                <td style="padding: 8px 0; color: #0066cc; font-weight: bold;">{calculation.get('pressure_required', 'N/A')} mbar</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Estimated Power:</strong></td>
                                <td style="padding: 8px 0;">{calculation.get('power_estimate', 'N/A')} kW</td>
                            </tr>
                        </table>
                    </div>

                    <!-- Recommendations -->
                    <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #2e7d32; margin-top: 0;">✓ We Found {len(products)} Matching Products</h3>
                        <p style="margin-bottom: 0;">Please review the attached PDF for complete product specifications, pricing, and availability.</p>
                    </div>

                    <!-- Call to Action -->
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #ffc107;">
                        <h3 style="color: #856404; margin-top: 0;">Ready to Order?</h3>
                        <p style="margin: 10px 0;">Our team is standing by to assist you with your blower selection.</p>
                        <div style="margin-top: 15px;">
                            <p style="margin: 5px 0;"><strong>Email:</strong> crelec@live.co.za</p>
                            <p style="margin: 5px 0;"><strong>Phone:</strong> +27 11 444 4555</p>
                            <p style="margin: 5px 0;"><strong>Website:</strong> www.crelec.co.za</p>
                        </div>
                    </div>

                    <!-- Footer -->
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <div style="text-align: center; color: #666; font-size: 12px;">
                        <p>This is an automated message from the Crelec Blower Selection Assistant</p>
                        <p style="margin-top: 10px;">Powered by Liberlocus</p>
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

Dear Customer,

Thank you for using our Blower Selection Assistant. Your customized quote is attached to this email.

QUOTE INFORMATION
-----------------
Quote Number: {quote_id}
Date: {datetime.now().strftime('%B %d, %Y')}
Valid Until: {valid_until}
Application: {customer_data.get('application', 'Industrial')}

YOUR REQUIREMENTS
-----------------
Tank Volume: {calculation.get('tank_volume', 'N/A')} m³
Required Airflow: {calculation.get('airflow_required', 'N/A')} m³/hr
Required Pressure: {calculation.get('pressure_required', 'N/A')} mbar
Estimated Power: {calculation.get('power_estimate', 'N/A')} kW

RECOMMENDATIONS
---------------
We found {len(products)} products that match your requirements.
Please see the attached PDF for complete details and pricing.

NEXT STEPS
----------
1. Review the attached PDF quote
2. Contact us if you have any questions
3. Reply to this email or call us to place your order

CONTACT US
----------
Email: crelec@live.co.za
Phone: +27 11 444 4555
Website: www.crelec.co.za

Best regards,
The Crelec S.A. Team

--
This is an automated message from the Crelec Blower Selection Assistant
Powered by Liberlocus
        """


# For testing
if __name__ == "__main__":
    print("""
    ========================================
    SENDGRID SETUP INSTRUCTIONS:
    ========================================

    1. Sign up at: https://signup.sendgrid.com/
       (Free tier: 100 emails/day)

    2. Get your API Key:
       - Login to SendGrid
       - Go to Settings > API Keys
       - Create API Key (Full Access)
       - Copy the key (starts with 'SG.')

    3. Add to Vercel:
       - Go to your Vercel project
       - Settings > Environment Variables
       - Add: SENDGRID_API_KEY = your-key-here
       - Redeploy

    That's it! Emails will send automatically.
    ========================================
    """)