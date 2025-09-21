"""
Flexible quote logger that adapts to any data structure
Automatically handles new fields as the calculator evolves
"""

from http.server import BaseHTTPRequestHandler
import json
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
        """Log any quote data flexibly"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length)
            quote_data = json.loads(body_data.decode('utf-8'))

            # Add metadata
            quote_data['_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'version': 'adaptive',
                'ip': self.headers.get('X-Forwarded-For', 'unknown'),
                'user_agent': self.headers.get('User-Agent', 'unknown')
            }

            # Flatten nested data for easier viewing
            flat_data = self.flatten_dict(quote_data)

            # Log to console with clear formatting
            print("\n" + "="*60)
            print("QUOTE GENERATED - v1.2.0+")
            print("="*60)
            for key, value in flat_data.items():
                if not key.startswith('_'):  # Skip metadata in main display
                    print(f"{key}: {value}")
            print("="*60 + "\n")

            # Save to JSON file (accumulates all quotes)
            self.save_to_json_log(flat_data)

            # Return success
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'success',
                'message': 'Quote logged (adaptive)',
                'fields_captured': len(flat_data)
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Logging error (non-critical): {e}")
            # Still return success to not break the flow
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'logged_with_warning',
                'message': str(e)
            }

            self.wfile.write(json.dumps(response).encode())

    def flatten_dict(self, d, parent_key='', sep='_'):
        """
        Flatten nested dictionary to make it easier to log/view
        Handles any structure automatically
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle lists (like products array)
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self.flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
                items.append((f"{new_key}_count", len(v)))
            else:
                items.append((new_key, v))

        return dict(items)

    def save_to_json_log(self, data):
        """
        Save to a cumulative JSON log file
        This creates a browsable record of all quotes
        """
        try:
            log_file = '/tmp/quotes_log.jsonl'  # JSON Lines format

            # Append to file (one JSON object per line)
            with open(log_file, 'a') as f:
                f.write(json.dumps(data) + '\n')

            # Also save last 100 quotes as array for easy viewing
            quotes_file = '/tmp/recent_quotes.json'
            recent_quotes = []

            try:
                # Read existing recent quotes
                with open(quotes_file, 'r') as f:
                    recent_quotes = json.load(f)
            except:
                recent_quotes = []

            # Add new quote and keep last 100
            recent_quotes.append(data)
            recent_quotes = recent_quotes[-100:]  # Keep last 100

            # Save back
            with open(quotes_file, 'w') as f:
                json.dump(recent_quotes, f, indent=2)

            print(f"Saved to log. Total recent quotes: {len(recent_quotes)}")

        except Exception as e:
            print(f"File logging skipped: {e}")


# Auto-export tool for future use
def export_quotes_to_csv():
    """
    Utility function to export all quotes to CSV
    Can be called periodically or on-demand
    """
    import csv

    try:
        with open('/tmp/recent_quotes.json', 'r') as f:
            quotes = json.load(f)

        if not quotes:
            return

        # Get all unique keys across all quotes
        all_keys = set()
        for quote in quotes:
            all_keys.update(quote.keys())

        # Sort keys for consistent column order
        fieldnames = sorted(list(all_keys))

        # Write CSV
        with open('/tmp/quotes_export.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(quotes)

        print(f"Exported {len(quotes)} quotes to CSV")

    except Exception as e:
        print(f"Export failed: {e}")


"""
BENEFITS OF THIS APPROACH:
=========================

1. **No Schema Required**
   - Automatically handles any new fields you add
   - No need to update database schema
   - Works with nested data structures

2. **Easy to View**
   - Clear console output in Vercel logs
   - Flattened structure for readability
   - Keeps recent quotes in JSON for quick access

3. **Future-Proof**
   - When ready, can export to any format
   - CSV export function included
   - Can migrate to database anytime

4. **Zero Configuration**
   - Works immediately
   - No Google Sheets setup needed now
   - No API keys required

5. **Development Friendly**
   - See exactly what data is captured
   - Easy to debug
   - No external dependencies

USAGE:
======
Just replace the call to /api/save_quote with /api/flexible_logger
Or keep both - one for current logging, one for flexible future logging

WHEN READY FOR PRODUCTION:
==========================
1. Decide on final data structure
2. Export accumulated quotes to CSV
3. Import to Google Sheets/Database
4. Set up proper schema then
"""