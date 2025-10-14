"""
Simple API endpoint to view logged inquiries
"""

from http.server import BaseHTTPRequestHandler
import json

try:
    from data_logger import data_logger
except ImportError:
    # Create a new instance if import fails
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data_logger import DataLogger
    data_logger = DataLogger()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request to view logs"""

        try:
            # Get all inquiries
            inquiries = data_logger.get_all_inquiries()
            stats = data_logger.get_summary_stats()
        except Exception as e:
            # If there's an error, return a simple error page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Inquiry Logs</title></head>
            <body style="font-family: Arial; padding: 40px;">
                <h1 style="color: #0066cc;">Crelec Inquiry Logs</h1>
                <div style="background: #f0f0f0; padding: 20px; border-radius: 8px;">
                    <h2>No Data Yet</h2>
                    <p>No inquiries have been logged yet. Complete a chatbot inquiry to see data here.</p>
                    <p style="color: #666; font-size: 0.9em;">Note: Data is stored temporarily on Vercel and may be cleared periodically.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
            return

        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Create HTML response
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crelec Inquiry Logs</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background: #f5f5f5;
                }}
                h1 {{
                    color: #0066cc;
                }}
                .stats {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-item {{
                    display: inline-block;
                    margin-right: 30px;
                    padding: 10px;
                    background: #f0f0f0;
                    border-radius: 5px;
                }}
                table {{
                    width: 100%;
                    background: white;
                    border-collapse: collapse;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th {{
                    background: #0066cc;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    position: sticky;
                    top: 0;
                }}
                td {{
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }}
                tr:hover {{
                    background: #f9f9f9;
                }}
                .download-btn {{
                    background: #28a745;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <h1>Crelec Blower Inquiry Logs</h1>

            <div class="stats">
                <h2>Summary Statistics</h2>
                <div class="stat-item">
                    <strong>Total Inquiries:</strong> {stats['total_inquiries']}
                </div>
                <div class="stat-item">
                    <strong>Avg Power:</strong> {stats['average_power']} kW
                </div>
                <div class="stat-item">
                    <strong>Last Inquiry:</strong> {stats.get('last_inquiry', 'N/A')}
                </div>
            </div>

            <a href="/api/export_logs" class="download-btn">📥 Download CSV</a>

            <h2>Recent Inquiries</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Quote ID</th>
                            <th>Email</th>
                            <th>Application</th>
                            <th>Environment</th>
                            <th>Airflow</th>
                            <th>Pressure</th>
                            <th>Power</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        # Add rows
        for inquiry in reversed(inquiries[-50:]):  # Show last 50 inquiries
            html += f"""
                        <tr>
                            <td>{inquiry.get('timestamp', '')}</td>
                            <td>{inquiry.get('quote_id', '')}</td>
                            <td>{inquiry.get('email', '')}</td>
                            <td>{inquiry.get('application', '')}</td>
                            <td>{inquiry.get('environment', '')}</td>
                            <td>{inquiry.get('airflow_m3_hr', '')} m³/hr</td>
                            <td>{inquiry.get('pressure_mbar', '')} mbar</td>
                            <td>{inquiry.get('power_kw', '')} kW</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <script>
                // Auto-refresh every 30 seconds
                setTimeout(() => location.reload(), 30000);
            </script>
        </body>
        </html>
        """

        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        """Handle OPTIONS request"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()