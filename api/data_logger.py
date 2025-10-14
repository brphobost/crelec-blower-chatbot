"""
Flexible data logging system that can export to multiple formats
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path

class DataLogger:
    """Flexible logger that can write to CSV, JSON, or send to webhooks"""

    def __init__(self, log_dir="logs"):
        """Initialize the logger with a directory for storing logs"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # CSV file path
        self.csv_file = self.log_dir / "inquiries.csv"
        self.json_file = self.log_dir / "inquiries.json"

    def log_inquiry(self, session_data, calculation_result):
        """Log an inquiry to CSV and JSON files"""

        # Create a flat dictionary with all data
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'quote_id': session_data.get('quote_id', ''),
            'email': session_data.get('email', ''),
            'application': session_data.get('application', ''),
            'environment': session_data.get('environment', ''),
            'operation_type': session_data.get('operation_type', ''),
            'altitude': session_data.get('altitude', ''),
            'location': session_data.get('location', ''),
            'num_tanks': session_data.get('num_tanks', ''),
            'tank_config': session_data.get('tank_config', ''),
            'length': session_data.get('length', ''),
            'width': session_data.get('width', ''),
            'height': session_data.get('height', ''),
            'pipe_diameter': session_data.get('pipe_diameter', ''),
            'pipe_length': session_data.get('pipe_length', ''),
            'num_bends': session_data.get('num_bends', ''),
            'diffuser_type': session_data.get('diffuser_type', ''),
            'airflow_m3_hr': round(calculation_result.get('airflow_m3_hr', 0), 1),
            'pressure_mbar': round(calculation_result.get('pressure_mbar', 0), 0),
            'power_kw': round(calculation_result.get('power_kw', 0), 1)
        }

        # Add any additional fields from session_data that aren't already included
        for key, value in session_data.items():
            if key not in log_entry and key != 'results':
                log_entry[f'extra_{key}'] = value

        # Log to CSV
        self._log_to_csv(log_entry)

        # Log to JSON
        self._log_to_json(log_entry)

        return log_entry

    def _log_to_csv(self, data):
        """Append data to CSV file, creating headers if needed"""

        file_exists = self.csv_file.exists()

        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())

            # Write headers if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(data)

    def _log_to_json(self, data):
        """Append data to JSON file"""

        # Load existing data
        if self.json_file.exists():
            with open(self.json_file, 'r') as f:
                try:
                    entries = json.load(f)
                except:
                    entries = []
        else:
            entries = []

        # Add new entry
        entries.append(data)

        # Save back
        with open(self.json_file, 'w') as f:
            json.dump(entries, f, indent=2)

    def get_all_inquiries(self):
        """Get all logged inquiries as a list of dictionaries"""

        if not self.csv_file.exists():
            return []

        inquiries = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                inquiries.append(row)

        return inquiries

    def export_to_google_sheets_format(self):
        """Export all data in a format ready for Google Sheets"""

        inquiries = self.get_all_inquiries()

        if not inquiries:
            return None

        # Create export file
        export_file = self.log_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            if inquiries:
                writer = csv.DictWriter(f, fieldnames=inquiries[0].keys())
                writer.writeheader()
                writer.writerows(inquiries)

        return export_file

    def get_summary_stats(self):
        """Get summary statistics of all inquiries"""

        inquiries = self.get_all_inquiries()

        if not inquiries:
            return {
                'total_inquiries': 0,
                'applications': {},
                'environments': {},
                'average_power': 0
            }

        # Calculate stats
        applications = {}
        environments = {}
        total_power = 0
        power_count = 0

        for inquiry in inquiries:
            # Count applications
            app = inquiry.get('application', 'unknown')
            applications[app] = applications.get(app, 0) + 1

            # Count environments
            env = inquiry.get('environment', 'unknown')
            environments[env] = environments.get(env, 0) + 1

            # Sum power
            try:
                power = float(inquiry.get('power_kw', 0))
                if power > 0:
                    total_power += power
                    power_count += 1
            except:
                pass

        return {
            'total_inquiries': len(inquiries),
            'applications': applications,
            'environments': environments,
            'average_power': round(total_power / power_count, 1) if power_count > 0 else 0,
            'last_inquiry': inquiries[-1].get('timestamp') if inquiries else None
        }

# Create a global instance
data_logger = DataLogger()

def log_inquiry(session_data, calculation_result):
    """Global function to log an inquiry"""
    return data_logger.log_inquiry(session_data, calculation_result)