"""
Export logs as CSV for download
"""

from http.server import BaseHTTPRequestHandler
from data_logger import data_logger
import csv
from io import StringIO

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Export all logs as CSV"""

        # Get all inquiries
        inquiries = data_logger.get_all_inquiries()

        if not inquiries:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"No data to export")
            return

        # Create CSV in memory
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=inquiries[0].keys())
        writer.writeheader()
        writer.writerows(inquiries)

        # Get CSV content
        csv_content = output.getvalue().encode('utf-8')

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'text/csv')
        self.send_header('Content-Disposition', 'attachment; filename="crelec_inquiries.csv"')
        self.send_header('Content-Length', str(len(csv_content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(csv_content)

    def do_OPTIONS(self):
        """Handle OPTIONS request"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()