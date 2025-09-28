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
                "Welcome! Let's select the right blower for your needs.\\n\\n"
                "First, what type of operation do you need?\\n\\n"
                "1️⃣ **Compression** (Blowing air into tanks, aeration)\\n"
                "2️⃣ **Vacuum** (Suction, extraction, conveying)\\n\\n"
                "Please type 1 for Compression or 2 for Vacuum:"
            )
            session['state'] = 'operation_type'

        elif session['state'] == 'operation_type':
            if '1' in message or 'compression' in message.lower():
                session['data']['operation'] = 'compression'
                response['message'] = (
                    "✅ Compression/Blowing selected.\\n\\n"
                    "Who will be handling the installation?\\n\\n"
                    "1️⃣ **Self** (DIY installation)\\n"
                    "2️⃣ **Consultant/Contractor** (Professional installation)\\n\\n"
                    "Please type 1 or 2:"
                )
                session['state'] = 'installation'
            elif '2' in message or 'vacuum' in message.lower():
                session['data']['operation'] = 'vacuum'
                response['message'] = (
                    "✅ Vacuum/Suction selected.\\n\\n"
                    "Who will be handling the installation?\\n\\n"
                    "1️⃣ **Self** (DIY installation)\\n"
                    "2️⃣ **Consultant/Contractor** (Professional installation)\\n\\n"
                    "Please type 1 or 2:"
                )
                session['state'] = 'installation'
            else:
                response['message'] = "Please type 1 for Compression or 2 for Vacuum:"

        elif session['state'] == 'installation':
            if '1' in message or 'self' in message.lower():
                session['data']['installation'] = 'self'
                install_msg = "Self-installation"
            elif '2' in message or 'consultant' in message.lower():
                session['data']['installation'] = 'consultant'
                install_msg = "Professional installation"
            else:
                response['message'] = "Please type 1 for Self or 2 for Consultant/Contractor:"
                return response

            response['message'] = (
                f"✅ {install_msg} noted.\\n\\n"
                "What's the altitude of your installation site?\\n"
                "You can provide:\\n"
                "• Altitude in meters (e.g., '1420m')\\n"
                "• City name (e.g., 'Johannesburg')\\n"
                "• 'Sea level' or 'coastal'\\n\\n"
                "Location or altitude:"
            )
            session['state'] = 'altitude'

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
                "1️⃣ **Waste Water Treatment** (aeration tanks)\\n"
                "2️⃣ **Fish Farming/Aquaculture**\\n"
                "3️⃣ **Industrial Process** (general)\\n\\n"
                "Please select 1-3:"
            )
            session['state'] = 'application'

        elif session['state'] == 'application':
            if '1' in message or 'waste' in message.lower():
                session['data']['application'] = 'waste_water'
                app_msg = "Waste Water Treatment"
            elif '2' in message or 'fish' in message.lower():
                session['data']['application'] = 'fish_hatchery'
                app_msg = "Fish Farming/Aquaculture"
            else:
                session['data']['application'] = 'industrial'
                app_msg = "Industrial Process"

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

                    # Set air changes based on application
                    app_type = session['data'].get('application', 'industrial')
                    if app_type == 'waste_water':
                        air_changes = 6
                        app_display = "Waste Water Treatment"
                    elif app_type == 'fish_hatchery':
                        air_changes = 10
                        app_display = "Fish Farming/Aquaculture"
                    else:
                        air_changes = 4
                        app_display = "Industrial Process"

                    airflow_required = round(tank_volume * air_changes * 1.2, 1)  # 1.2 safety factor

                    # Pressure calculation
                    water_pressure = height * 98.1
                    system_losses = 150
                    altitude = session['data'].get('altitude', 500)
                    altitude_correction = (altitude / 100) * 12
                    pressure_required = round(water_pressure + system_losses + altitude_correction, 1)

                    # Power estimate
                    power_estimate = round((airflow_required / 3600) * pressure_required / 600, 2)

                    # Store calculation results
                    session['calculation'] = {
                        'airflow_required': airflow_required,
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