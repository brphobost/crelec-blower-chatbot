"""
Configuration file for API settings
COPY THIS FILE TO config.py AND UPDATE WITH YOUR SETTINGS
"""

# Google Sheets Webhook URL
# To enable Google Sheets logging:
# 1. Follow the steps in GOOGLE_SHEETS_SETUP.md
# 2. Create your Google Apps Script webhook
# 3. Copy this file to config.py
# 4. Paste your webhook URL below
GOOGLE_SHEETS_WEBHOOK = ""

# Example URL format:
# GOOGLE_SHEETS_WEBHOOK = "https://script.google.com/macros/s/AKfycbwXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/exec"

# Email settings (for future use)
SEND_EMAIL_NOTIFICATIONS = False
NOTIFICATION_EMAIL = "sales@crelec.co.za"