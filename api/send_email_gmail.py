"""
Gmail-based email sending for Crelec Blower Chatbot
Quick setup version - just add your Gmail credentials
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

# ====== CONFIGURATION - CHANGE THESE ======
GMAIL_USER = "your.email@gmail.com"  # Your Gmail address
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"  # Your 16-character app password
ADMIN_EMAIL = "crelec@live.co.za"  # Admin email to CC
# ==========================================

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

            # Create message
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = to_email
            msg['Cc'] = ADMIN_EMAIL
            msg['Subject'] = f'Crelec Blower Quote #{quote_id}'

            # Email body (HTML version)
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #1a3e4c; color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0;">CRELEC S.A.</h1>
                        <p style="margin: 5px 0;">Side Channel Blowers & Vacuum Pumps</p>
                    </div>

                    <div style="padding: 20px; background: #f9f9f9;">
                        <h2 style="color: #1a3e4c;">Your Blower Quote is Ready!</h2>

                        <p>Dear Customer,</p>

                        <p>Thank you for using our Blower Selection Assistant. Your personalized quote is attached to this email.</p>

                        <div style="background: white; padding: 15px; border-left: 4px solid #1a3e4c; margin: 20px 0;">
                            <h3 style="color: #1a3e4c; margin-top: 0;">Quote Details:</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><strong>Quote ID:</strong> {quote_id}</li>
                                <li><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</li>
                                <li><strong>Valid Until:</strong> {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}</li>
                            </ul>
                        </div>

                        <div style="background: white; padding: 15px; border-left: 4px solid #0066cc; margin: 20px 0;">
                            <h3 style="color: #0066cc; margin-top: 0;">Your Requirements:</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li><strong>Tank Volume:</strong> {calculation.get('tank_volume', 'N/A')} m³</li>
                                <li><strong>Required Airflow:</strong> {calculation.get('airflow_required', 'N/A')} m³/hr</li>
                                <li><strong>Required Pressure:</strong> {calculation.get('pressure_required', 'N/A')} mbar</li>
                                <li><strong>Estimated Power:</strong> {calculation.get('power_estimate', 'N/A')} kW</li>
                            </ul>
                        </div>

                        <p><strong>We have recommended {len(products)} products</strong> that match your requirements. Please see the attached PDF for complete details and pricing.</p>

                        <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #2e7d32; margin-top: 0;">Next Steps:</h3>
                            <ol>
                                <li>Review the attached PDF quote</li>
                                <li>Contact us if you have any questions</li>
                                <li>Reply to this email to place your order</li>
                            </ol>
                        </div>

                        <div style="text-align: center; margin: 30px 0;">
                            <p><strong>Ready to Order?</strong></p>
                            <p style="margin: 5px;">Email: {ADMIN_EMAIL}</p>
                            <p style="margin: 5px;">Phone: +27 11 444 4555</p>
                        </div>

                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                        <div style="text-align: center; color: #666; font-size: 12px;">
                            <p>This is an automated message from the Crelec Blower Selection Assistant</p>
                            <p>Powered by Liberlocus</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text version
            plain_body = f"""
Dear Customer,

Thank you for using our Blower Selection Assistant. Your personalized quote is attached.

QUOTE DETAILS:
--------------
Quote ID: {quote_id}
Date: {datetime.now().strftime('%B %d, %Y')}

YOUR REQUIREMENTS:
Tank Volume: {calculation.get('tank_volume', 'N/A')} m³
Required Airflow: {calculation.get('airflow_required', 'N/A')} m³/hr
Required Pressure: {calculation.get('pressure_required', 'N/A')} mbar
Estimated Power: {calculation.get('power_estimate', 'N/A')} kW

We have recommended {len(products)} products that match your requirements.
Please see the attached PDF for complete details and pricing.

For questions or to place an order:
Email: {ADMIN_EMAIL}
Phone: +27 11 444 4555

Best regards,
Crelec S.A. Team

--
This is an automated message from the Crelec Blower Selection Assistant
Powered by Liberlocus
            """

            # Attach both HTML and plain text versions
            msg.attach(MIMEText(plain_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Attach PDF if provided
            if pdf_base64:
                pdf_data = base64.b64decode(pdf_base64)
                attachment = MIMEBase('application', 'pdf')
                attachment.set_payload(pdf_data)
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition',
                                    f'attachment; filename="Crelec_Quote_{quote_id}.pdf"')
                msg.attach(attachment)

            # Send email via Gmail
            try:
                # Get credentials from environment variables if available
                gmail_user = os.getenv('GMAIL_USER', GMAIL_USER)
                gmail_pass = os.getenv('GMAIL_APP_PASSWORD', GMAIL_APP_PASSWORD).replace(' ', '')

                # Connect to Gmail
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(gmail_user, gmail_pass)

                # Send email
                recipients = [to_email, ADMIN_EMAIL]
                server.send_message(msg)
                server.quit()

                email_sent = True
                message = f'Email sent successfully to {to_email} with CC to admin'
            except Exception as email_error:
                print(f"Email sending error: {email_error}")
                email_sent = False
                message = f'Email sending pending configuration. PDF downloaded successfully.'

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


# For local testing
if __name__ == "__main__":
    print("""
    ========================================
    GMAIL SETUP INSTRUCTIONS:
    ========================================

    1. Go to your Gmail account settings
    2. Enable 2-Factor Authentication
    3. Generate App Password:
       - Visit: https://myaccount.google.com/apppasswords
       - Select 'Mail' and generate
       - Copy the 16-character password

    4. Update this file:
       - Set GMAIL_USER to your Gmail address
       - Set GMAIL_APP_PASSWORD to the generated password

    5. For Vercel deployment:
       - Add these as environment variables in Vercel dashboard

    ========================================
    """)

from datetime import timedelta