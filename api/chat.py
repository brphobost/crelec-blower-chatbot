from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import uuid
import re

# In-memory storage for sessions
sessions = {}

import urllib.request
import urllib.parse

# Load products from Google Sheets or fallback to JSON
def load_products():
    """Load products from Google Sheets or fallback to local JSON"""
    try:
        # Try to load from Google Sheets first
        SHEET_ID = "14x7T9cHol94jk3w4CgZggKIYrYSMpefRrflYfC0HUk4"
        SHEET_NAME = "Sheet1"

        # Build Google Sheets API URL (using visualization API for public sheets)
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={SHEET_NAME}"

        # Fetch data from Google Sheets
        with urllib.request.urlopen(csv_url) as response:
            raw_data = response.read().decode('utf-8')

        # Parse Google Visualization API response
        # Remove the JavaScript wrapper to get JSON
        json_str = raw_data.split('(', 1)[1].rsplit(')', 1)[0]
        data = json.loads(json_str)

        # Convert to our product format
        products = []
        rows = data['table']['rows']

        # Skip header row, process data rows
        for row in rows[1:]:  # Assuming first row is headers
            try:
                cells = row['c']
                # Match simplified format: Model, Airflow, Pressure, Power, In Stock
                if cells[0] and cells[0].get('v'):  # Check model exists
                    airflow_m3_min = float(cells[1]['v']) if cells[1] and cells[1].get('v') else 0
                    product = {
                        'model': cells[0]['v'],
                        'airflow_m3_min': airflow_m3_min,  # Keep in m³/min
                        'airflow': airflow_m3_min * 60,  # Also store in m³/hr for compatibility
                        'pressure': float(cells[2]['v']) if cells[2] and cells[2].get('v') else 0,
                        'power': float(cells[3]['v']) if cells[3] and cells[3].get('v') else 0,
                        'in_stock': str(cells[4]['v']).lower() == 'yes' if cells[4] and cells[4].get('v') else False
                    }

                    # Only add if essential fields are present
                    if product['model'] and airflow_m3_min > 0:
                        products.append(product)
            except (IndexError, KeyError, ValueError, TypeError) as e:
                continue  # Skip malformed rows

        print(f"Loaded {len(products)} products from Google Sheets")
        return products

    except Exception as e:
        print(f"Error loading from Google Sheets: {e}, falling back to local JSON")
        # Fallback to local JSON
        try:
            with open('frontend/products_simplified.json', 'r') as f:
                products_data = json.load(f)
                return products_data['products']
        except:
            try:
                with open('frontend/products.json', 'r') as f:
                    products_data = json.load(f)
                    # Convert old format to simplified format
                    simplified = []
                    for p in products_data['products']:
                        simplified.append({
                            'model': p.get('model', ''),
                            'airflow': (p.get('airflow_min', 0) + p.get('airflow_max', 0)) / 2,
                            'pressure': (p.get('pressure_min', 0) + p.get('pressure_max', 0)) / 2,
                            'power': p.get('power', 0),
                            'in_stock': p.get('stock_status') == 'in_stock'
                        })
                    return simplified
            except Exception as e:
                print(f"Error loading products: {e}")
                return []  # Return empty list if loading fails

PRODUCTS = load_products()

def match_products(airflow_required, pressure_required):
    """Smart product matching with simplified catalog format

    Args:
        airflow_required: Required airflow in m³/min
        pressure_required: Required pressure in mbar
    """
    matches = []

    for product in PRODUCTS:
        # Skip if product doesn't have required fields
        if not all(k in product for k in ['airflow_m3_min', 'pressure', 'power']):
            # Try alternative field names
            if not all(k in product for k in ['airflow', 'pressure', 'power']):
                continue

        score = 0
        match_type = ""

        # Get product specs in m³/min
        product_airflow = product.get('airflow_m3_min', product.get('airflow', 0) / 60)  # Convert if needed
        product_pressure = product.get('pressure', 0)

        # Check if product meets minimum requirements
        if product_airflow >= airflow_required and product_pressure >= pressure_required:
            # Calculate how much oversized the product is
            airflow_excess = (product_airflow - airflow_required) / airflow_required if airflow_required > 0 else 0
            pressure_excess = (product_pressure - pressure_required) / pressure_required if pressure_required > 0 else 0

            # Perfect match (within 20% oversized)
            if airflow_excess <= 0.2 and pressure_excess <= 0.2:
                score = 100
                match_type = "Perfect Match"
            # Good match (within 50% oversized)
            elif airflow_excess <= 0.5 and pressure_excess <= 0.5:
                score = 80
                match_type = "Recommended"
            # Acceptable match (meets requirements but oversized)
            else:
                score = 60 - (airflow_excess * 10) - (pressure_excess * 10)
                match_type = "Higher Capacity Option"

        # For very small requirements, recommend smallest suitable blower
        elif product_pressure >= pressure_required:
            # Product meets pressure but not airflow - still consider it
            score = 40 - (airflow_required - product_airflow) / 10
            match_type = "Minimum Available"

        # Stock status bonus
        if score > 0:
            if product.get('in_stock', False):
                score += 10
            else:
                score -= 5

            matches.append({
                'product': product,
                'score': score,
                'match_type': match_type
            })

    # Sort by score and return top 3
    matches.sort(key=lambda x: x['score'], reverse=True)

    # If no matches found, return closest alternatives
    if len(matches) == 0 and len(PRODUCTS) > 0:
        # Find products with sufficient pressure at least
        for product in PRODUCTS:
            if product.get('pressure', 0) >= pressure_required * 0.5:  # At least 50% of pressure
                matches.append({
                    'product': product,
                    'score': 10,
                    'match_type': 'Alternative Option'
                })

        # If still no matches, just show any products
        if len(matches) == 0:
            for product in PRODUCTS[:3]:
                matches.append({
                    'product': product,
                    'score': 1,
                    'match_type': 'Available Product'
                })

    return matches[:3]

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        session_id = data.get('session_id')
        message = data.get('message', '').strip()

        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {
                'state': 'welcome',
                'data': {},
                'calculation': {}
            }

        session = sessions[session_id]
        response = {'session_id': session_id}

        # State machine for conversation flow
        if session['state'] == 'welcome':
            response['message'] = (
                "Welcome! Let's select the right blower for your needs.\\n\\n"
                "First, what type of operation do you need?\\n\\n"
                "• **Compression** (Blowing air into tanks, aeration)\\n"
                "• **Vacuum** (Suction, extraction, conveying)\\n\\n"
                "Please type 'compression' or 'vacuum':"
            )
            session['state'] = 'operation_type'

        elif session['state'] == 'operation_type':
            msg_lower = message.lower().strip()
            if 'comp' in msg_lower or 'blow' in msg_lower or 'aerat' in msg_lower:
                session['data']['operation'] = 'compression'
                op_msg = "Compression/Blowing"
            elif 'vac' in msg_lower or 'suc' in msg_lower or 'extract' in msg_lower:
                session['data']['operation'] = 'vacuum'
                op_msg = "Vacuum/Suction"
            else:
                response['message'] = (
                    "I didn't understand that. Please type:\\n"
                    "• 'compression' for blowing/aeration\\n"
                    "• 'vacuum' for suction/extraction"
                )
                self.wfile.write(json.dumps(response).encode())
                return

            response['message'] = (
                f"✅ {op_msg} selected.\\n\\n"
                "What's the altitude of your installation site?\\n"
                "You can provide:\\n"
                "• Altitude in meters (e.g., '1420m')\\n"
                "• City name (e.g., 'Johannesburg')\\n"
                "• 'Sea level' or 'coastal'\\n\\n"
                "Location or altitude:"
            )
            session['state'] = 'altitude'

        # Installation step removed - not used in calculations

        elif session['state'] == 'altitude':
            # Store altitude info
            session['data']['altitude_text'] = message
            # Simple altitude parsing (will be enhanced with location handler)
            try:
                altitude = float(re.findall(r'\d+', message)[0]) if re.findall(r'\d+', message) else 500
            except:
                altitude = 500
            session['data']['altitude'] = altitude

            response['message'] = (
                f"✅ Location confirmed: {altitude}m altitude\\n\\n"
                "What's your application?\\n\\n"
                "• **Waste Water** Treatment (aeration tanks)\\n"
                "• **Fish** Farming/Aquaculture\\n"
                "• **Industrial** Process (general)\\n\\n"
                "Please type 'waste water', 'fish', or 'industrial':"
            )
            session['state'] = 'application'

        elif session['state'] == 'application':
            msg_lower = message.lower().strip()
            if 'waste' in msg_lower or 'water treat' in msg_lower or 'aerat' in msg_lower:
                session['data']['application'] = 'waste_water'
                app_msg = "Waste Water Treatment"
            elif 'fish' in msg_lower or 'aqua' in msg_lower or 'hatch' in msg_lower:
                session['data']['application'] = 'fish_hatchery'
                app_msg = "Fish Farming/Aquaculture"
            elif 'industr' in msg_lower or 'process' in msg_lower or 'general' in msg_lower:
                session['data']['application'] = 'industrial'
                app_msg = "Industrial Process"
            else:
                response['message'] = (
                    "I didn't understand that. Please type:\\n"
                    "• 'waste water' for treatment plants\\n"
                    "• 'fish' for aquaculture\\n"
                    "• 'industrial' for general processes"
                )
                self.wfile.write(json.dumps(response).encode())
                return

            response['message'] = (
                f"✅ {app_msg} selected.\\n\\n"
                "**OPERATIONAL DATA**\\n\\n"
                "Let's start with your tank/system dimensions.\\n"
                "Please provide tank size in meters:\\n\\n"
                "• Length × Width × Depth (e.g., '6 3 2')\\n\\n"
                "Tank dimensions:"
            )
            session['state'] = 'dimensions'

        elif session['state'] == 'dimensions':
            try:
                parts = message.replace(',', ' ').replace('x', ' ').replace('×', ' ').split()
                if len(parts) >= 3:
                    length, width, height = map(float, parts[:3])
                    session['data']['length'] = length
                    session['data']['width'] = width
                    session['data']['height'] = height

                    # Calculate requirements
                    tank_volume = length * width * height
                    tank_area = length * width  # m²

                    # Calculate airflow based on application (using formulas from reference)
                    app_type = session['data'].get('application', 'industrial')
                    if app_type == 'waste_water':
                        # Waste water: Q = tank area × 0.25 m³/min
                        airflow_m3_min = tank_area * 0.25
                        app_display = "Waste Water Treatment"
                    elif app_type == 'fish_hatchery':
                        # Fish hatchery: Q = pond area × (0.0015 to 0.0025) m³/min
                        # Using middle value 0.002
                        airflow_m3_min = tank_area * 0.002
                        app_display = "Fish Farming/Aquaculture"
                    else:
                        # Industrial: Using conservative estimate
                        airflow_m3_min = tank_area * 0.1
                        app_display = "Industrial Process"

                    # Keep in m³/min for calculations and display
                    airflow_required = round(airflow_m3_min, 3)  # m³/min

                    # Pressure calculation based on formulas
                    # P = tank depth H(cm) × solution specific gravity r × (1.2~1.5)
                    # Converting: H(cm) × 1 × 1.3 = H(m) × 100 × 1.3 = H(m) × 130 mbar

                    depth_pressure = height * 100 * 1.3  # depth in cm × gravity × safety factor

                    # Add system losses (pipes, diffusers)
                    system_losses = 50  # Reduced from 150 as depth pressure includes safety

                    # Altitude correction
                    altitude = session['data'].get('altitude', 500)
                    altitude_correction = (altitude / 100) * 12

                    pressure_required = round(depth_pressure + system_losses + altitude_correction, 1)

                    # Power estimate
                    power_estimate = round((airflow_required / 3600) * pressure_required / 600, 2)

                    # Store calculation results
                    session['calculation'] = {
                        'airflow_required': airflow_required,  # m³/min
                        'airflow_required_hr': airflow_required * 60,  # m³/hr for display
                        'pressure_required': pressure_required,
                        'power_estimate': power_estimate,
                        'tank_volume': round(tank_volume, 1),
                        'application_type': app_display
                    }

                    # Get matched products
                    matched_products = match_products(airflow_required, pressure_required)
                    session['matched_products'] = matched_products

                    # Set state to email collection
                    session['state'] = 'email'

                    response['message'] = (
                        f"✅ Tank dimensions: {length}m × {width}m × {height}m = {tank_volume:.0f}m³\\n\\n"
                        f"**Calculation Complete!**\\n\\n"
                        f"Based on your requirements:\\n"
                        f"• Tank Volume: {round(tank_volume, 1)} m³\\n"
                        f"• Required Airflow: {airflow_required} m³/min ({airflow_required * 60:.1f} m³/hr)\\n"
                        f"• Required Pressure: {pressure_required} mbar\\n"
                        f"• Estimated Power: {power_estimate} kW\\n\\n"
                        f"I've found {len(matched_products)} perfect blowers for your needs!\\n\\n"
                        f"To receive your detailed quote with:\\n"
                        f"• Technical specifications\\n"
                        f"• Pricing and availability\\n"
                        f"• Delivery times\\n"
                        f"• Valid for 30 days\\n\\n"
                        f"Please enter your email address:"
                    )
                else:
                    response['message'] = "Please enter three numbers for length, width, and height (e.g., '6 3 2'):"
            except ValueError:
                response['message'] = "Please enter three valid numbers in meters (e.g., '6 3 2'):"

        # Note: 'complete' state removed - calculation now happens in dimensions state

        elif session['state'] == 'email':
            # Validate email
            if validate_email(message):
                session['data']['email'] = message

                # Generate quote ID
                quote_id = f"Q{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                session['quote_id'] = quote_id

                # Format products for display
                products_summary = []
                for i, match in enumerate(session.get('matched_products', [])[:3], 1):
                    product = match['product']
                    stock_emoji = "✅" if product.get('in_stock', False) else "⏱️"
                    stock_text = "In Stock" if product.get('in_stock', False) else "On Order"

                    # Get airflow in correct units
                    airflow_m3_min = product.get('airflow_m3_min', product.get('airflow', 0) / 60)
                    airflow_m3_hr = airflow_m3_min * 60

                    products_summary.append(
                        f"{i}. **{product['model']}** - {match['match_type']}\\n"
                        f"   Airflow: {airflow_m3_min:.1f} m³/min ({airflow_m3_hr:.0f} m³/hr)\\n"
                        f"   Pressure: {product.get('pressure', 0):.0f} mbar | Power: {product.get('power', 0)} kW\\n"
                        f"   {stock_emoji} {stock_text}"
                    )

                response['message'] = (
                    f"📧 **Thank you!**\\n\\n"
                    f"Your detailed quote #{quote_id} will be sent to:\\n"
                    f"📨 {message}\\n\\n"
                    f"**Your recommended blowers:**\\n\\n" +
                    "\\n\\n".join(products_summary) +
                    f"\\n\\n**What happens next:**\\n"
                    f"• You'll receive a detailed PDF quote\\n"
                    f"• Our team will be notified\\n"
                    f"• Someone may follow up within 24 hours\\n\\n"
                    f"**Need immediate assistance?**\\n"
                    f"📞 Call: +27 11 444 4555\\n"
                    f"📧 Email: crelec@live.co.za"
                )

                # Prepare for sending email (will be handled by frontend)
                response['send_email'] = True
                response['email_data'] = {
                    'to': message,
                    'cc': 'crelec@live.co.za',
                    'quote_id': quote_id,
                    'calculation': session['calculation'],
                    'products': session['matched_products'],
                    'customer_data': session['data']
                }

                session['state'] = 'complete'

            else:
                response['message'] = (
                    "Please enter a valid email address (e.g., john@example.com):"
                )

        elif session['state'] == 'complete':
            if 'new' in message.lower() or 'start' in message.lower():
                # Reset session for new calculation
                sessions[session_id] = {
                    'state': 'operation_type',
                    'data': {},
                    'calculation': {}
                }
                response['message'] = (
                    "Welcome! Let's select the right blower for your needs.\\n\\n"
                    "First, what type of operation do you need?\\n\\n"
                    "• **Compression** (Blowing air into tanks, aeration)\\n"
                    "• **Vacuum** (Suction, extraction, conveying)\\n\\n"
                    "Please type 'compression' or 'vacuum':"
                )
            else:
                response['message'] = (
                    "Your quote has been sent!\\n\\n"
                    "Would you like to:\\n"
                    "• Start a new calculation (type 'new')\\n"
                    "• Contact support (call +27 11 444 4555)"
                )

        # Send response
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # API status endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "name": "Crelec Blower Selection API",
            "version": "2.0.0",
            "status": "operational",
            "features": ["product_matching", "email_quotes"]
        }
        self.wfile.write(json.dumps(response).encode())