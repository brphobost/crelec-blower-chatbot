from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import uuid
import re

# In-memory storage for sessions
sessions = {}

# Load products from JSON
with open('frontend/products.json', 'r') as f:
    products_data = json.load(f)
    PRODUCTS = products_data['products']

def match_products(airflow_required, pressure_required):
    """Smart product matching with scoring system"""
    matches = []

    for product in PRODUCTS:
        score = 0
        match_type = ""

        # Perfect match (100 points)
        if (product['airflow_min'] <= airflow_required <= product['airflow_max'] and
            product['pressure_min'] <= pressure_required <= product['pressure_max']):
            score = 100
            match_type = "Perfect Match"

        # Over-specified but within 20% (80 points)
        elif (airflow_required >= product['airflow_min'] * 0.8 and
              pressure_required >= product['pressure_min'] * 0.8 and
              airflow_required <= product['airflow_max'] and
              pressure_required <= product['pressure_max']):
            score = 80
            match_type = "Recommended"

        # Slightly over capacity (70 points)
        elif (product['airflow_max'] >= airflow_required and
              product['pressure_max'] >= pressure_required and
              product['airflow_min'] <= airflow_required * 1.3):
            score = 70
            match_type = "Higher Capacity Option"

        # Stock status bonus
        if score > 0:
            if product['stock_status'] == 'in_stock':
                score += 10
            elif product['stock_status'] == 'low_stock':
                score += 5
            elif product['stock_status'] == 'on_order':
                score -= 10

            matches.append({
                'product': product,
                'score': score,
                'match_type': match_type
            })

    # Sort by score and return top 3
    matches.sort(key=lambda x: x['score'], reverse=True)
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
                "Hi! I'll help you select the right blower for your needs. "
                "Let's start with your tank dimensions. "
                "Please enter the length, width, and height in meters (e.g., '6 3 2'):"
            )
            session['state'] = 'dimensions'

        elif session['state'] == 'dimensions':
            try:
                parts = message.replace(',', ' ').split()
                if len(parts) >= 3:
                    length, width, height = map(float, parts[:3])
                    session['data'] = {'length': length, 'width': width, 'height': height}
                    session['state'] = 'altitude'
                    response['message'] = (
                        f"Got it! Tank dimensions: {length}m × {width}m × {height}m\\n"
                        "Now, what's your facility's altitude above sea level in meters?"
                    )
                else:
                    response['message'] = "Please enter three numbers for length, width, and height."
            except ValueError:
                response['message'] = "Please enter three valid numbers in meters (e.g., '6 3 2'):"

        elif session['state'] == 'altitude':
            try:
                altitude = float(message.split()[0])
                session['data']['altitude'] = altitude
                session['state'] = 'application'
                response['message'] = (
                    f"Altitude set to {altitude}m above sea level.\\n"
                    "What's your application? Choose one:\\n"
                    "1. Waste Water Treatment\\n"
                    "2. Fish Hatchery\\n"
                    "3. General Industrial"
                )
            except ValueError:
                session['data']['altitude'] = 500
                session['state'] = 'application'
                response['message'] = (
                    "I'll use 500m as the altitude for now.\\n"
                    "What's your application? Choose one:\\n"
                    "1. Waste Water Treatment\\n"
                    "2. Fish Hatchery\\n"
                    "3. General Industrial"
                )

        elif session['state'] == 'application':
            # Determine application type
            msg_lower = message.lower()
            if '1' in msg_lower or 'waste' in msg_lower:
                app_type = 'waste_water'
                air_changes = 6
            elif '2' in msg_lower or 'fish' in msg_lower:
                app_type = 'fish_hatchery'
                air_changes = 10
            else:
                app_type = 'general'
                air_changes = 4

            session['data']['application_type'] = app_type

            # Calculate requirements
            data = session['data']
            tank_volume = data['length'] * data['width'] * data['height']
            airflow_required = round(tank_volume * air_changes * 1.2, 1)  # 1.2 safety factor

            # Pressure calculation
            water_pressure = data['height'] * 98.1
            system_losses = 150
            altitude_correction = (data['altitude'] / 100) * 12
            pressure_required = round(water_pressure + system_losses + altitude_correction, 1)

            # Power estimate
            power_estimate = round((airflow_required / 3600) * pressure_required / 600, 2)

            # Store calculation results
            session['calculation'] = {
                'airflow_required': airflow_required,
                'pressure_required': pressure_required,
                'power_estimate': power_estimate,
                'tank_volume': round(tank_volume, 1),
                'application_type': app_type
            }

            # Get matched products
            matched_products = match_products(airflow_required, pressure_required)
            session['matched_products'] = matched_products

            # Ask for email
            session['state'] = 'email'

            response['message'] = (
                f"✅ **Calculation Complete!**\\n\\n"
                f"Based on your requirements:\\n"
                f"• Tank Volume: {round(tank_volume, 1)} m³\\n"
                f"• Required Airflow: {airflow_required} m³/hr\\n"
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
                    stock_emoji = "✅" if product['stock_status'] == 'in_stock' else "⏱️"
                    delivery = "Immediate delivery" if product['delivery_days'] == 0 else f"{product['delivery_days']} days delivery"

                    products_summary.append(
                        f"{i}. **{product['model']}** - {match['match_type']}\\n"
                        f"   Power: {product['power']} kW | R {product['price']:,}\\n"
                        f"   {stock_emoji} {delivery}"
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
            if 'new' in message.lower():
                # Reset session for new calculation
                sessions[session_id] = {
                    'state': 'welcome',
                    'data': {},
                    'calculation': {}
                }
                response['message'] = (
                    "Starting a new calculation. "
                    "Please enter your tank dimensions in meters (length width height):"
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