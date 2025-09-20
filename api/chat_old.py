from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import uuid

# In-memory storage for sessions
sessions = {}

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
                'data': {}
            }

        session = sessions[session_id]
        response = {'session_id': session_id}

        # Simple state machine
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

            # Generate quote ID
            quote_id = f"Q{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            # Product recommendations (simplified)
            products = []
            if airflow_required <= 700 and pressure_required <= 450:
                products.append({
                    'model': 'Griffin G20 36 2RB',
                    'power': 4.0,
                    'price': 'R38,000',
                    'stock': 'In Stock'
                })
            if 500 <= airflow_required <= 800 and 300 <= pressure_required <= 500:
                products.append({
                    'model': 'Griffin GIS 36 2RB',
                    'power': 5.5,
                    'price': 'R45,000',
                    'stock': 'In Stock'
                })
            if airflow_required > 600:
                products.append({
                    'model': 'HB5515',
                    'power': 7.5,
                    'price': 'R52,000',
                    'stock': '2 weeks delivery'
                })

            # Format response
            response['message'] = f"""✅ **Calculation Complete!** Quote ID: {quote_id}

**Your Requirements:**
- Airflow: {airflow_required} m³/hr
- Pressure: {pressure_required} mbar
- Estimated Power: {power_estimate} kW
- Tank Volume: {round(tank_volume, 1)} m³

**Recommended Blowers:**"""

            for i, product in enumerate(products[:3], 1):
                response['message'] += f"""
{i}. **{product['model']}**
   - Power: {product['power']} kW
   - Price: {product['price']}
   - Status: {product['stock']}"""

            response['calculation'] = {
                'success': True,
                'results': {
                    'airflow_required': airflow_required,
                    'pressure_required': pressure_required,
                    'power_estimate': power_estimate,
                    'tank_volume': round(tank_volume, 1)
                }
            }
            response['products'] = products
            response['quote_id'] = quote_id

            session['state'] = 'complete'

        elif session['state'] == 'complete':
            if 'new' in message.lower():
                session['state'] = 'welcome'
                session['data'] = {}
                response['message'] = (
                    "Starting a new calculation. "
                    "Please enter your tank dimensions in meters (length width height):"
                )
            else:
                response['message'] = (
                    "Would you like to:\\n"
                    "1. Start a new calculation (type 'new')\\n"
                    "2. Get help from a human expert (type 'help')"
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
            "version": "1.0.0",
            "status": "operational"
        }
        self.wfile.write(json.dumps(response).encode())