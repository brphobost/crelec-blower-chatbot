"""
Email sending API endpoint for the Crelec Blower Chatbot
Uses server-side email sending to avoid exposing API keys
"""

from http.server import BaseHTTPRequestHandler
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
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

            # Compose email
            msg = MIMEMultipart()
            msg['From'] = 'noreply@crelec.co.za'
            msg['To'] = to_email
            msg['Cc'] = 'crelec@live.co.za'
            msg['Subject'] = f'Crelec Blower Quote #{quote_id}'

            # Email body
            body = f"""
Dear Customer,

Thank you for using our Blower Selection Assistant. Please find attached your personalized quote.

QUOTE DETAILS:
--------------
Quote ID: {quote_id}
Date: {datetime.now().strftime('%Y-%m-%d')}

REQUIREMENTS:
Tank Volume: {calculation.get('tank_volume', 'N/A')} m³
Required Airflow: {calculation.get('airflow_required', 'N/A')} m³/hr
Required Pressure: {calculation.get('pressure_required', 'N/A')} mbar
Estimated Power: {calculation.get('power_estimate', 'N/A')} kW

We have recommended {len(products)} products that match your requirements.
Please see the attached PDF for complete details and pricing.

For any questions or to place an order, please contact us:
📧 Email: crelec@live.co.za
📞 Phone: +27 11 444 4555

Best regards,
Crelec S.A. Team

--
This is an automated message from the Crelec Blower Selection Assistant
Powered by Liberlocus
            """

            msg.attach(MIMEText(body, 'plain'))

            # Attach PDF if provided
            if pdf_base64:
                pdf_data = base64.b64decode(pdf_base64)
                attachment = MIMEBase('application', 'pdf')
                attachment.set_payload(pdf_data)
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition',
                                    f'attachment; filename="Crelec_Quote_{quote_id}.pdf"')
                msg.attach(attachment)

            # For now, just return success without actually sending
            # In production, you'd configure SMTP settings here:
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login('your-email@gmail.com', 'your-password')
            # server.send_message(msg)
            # server.quit()

            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'success',
                'message': 'Email functionality coming soon. PDF has been downloaded to your device.',
                'quote_id': quote_id,
                'note': 'For immediate assistance, please email crelec@live.co.za with your quote ID'
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