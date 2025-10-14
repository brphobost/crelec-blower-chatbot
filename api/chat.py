"""
Enhanced Chat Handler for Vercel Deployment
Includes pipe system, diffuser selection, and multiple tanks
Uses the enhanced calculator for professional calculations
"""

from http.server import BaseHTTPRequestHandler
import json
import re
import uuid

try:
    from enhanced_calculator import EnhancedBlowerCalculator
    USING_ENHANCED = True
except ImportError as e:
    # Fallback if module not found
    USING_ENHANCED = False
    print(f"Failed to import enhanced_calculator: {e}")
    class EnhancedBlowerCalculator:
        def calculate(self, **kwargs):
            # Simple fallback calculation
            airflow = kwargs.get('tank_length', 6) * kwargs.get('tank_width', 3) * 0.25 * 60
            altitude = kwargs.get('altitude', 0)
            environment_factor = kwargs.get('environment_factor', 1.0)

            # Calculate altitude correction (1% per 100m)
            altitude_correction = 1 + (altitude / 100 / 100) if altitude > 0 else 1.0

            # Base pressure calculation
            base_pressure = kwargs.get('tank_depth', 2) * 100 + 250 + 15 + 10  # static + diffuser + pipes
            safety_factor = 1.10  # 10% base safety
            safety_margin = base_pressure * (safety_factor - 1)
            environment_adjustment = base_pressure * (environment_factor - 1) if environment_factor > 1.0 else 0

            # Apply all corrections
            total_pressure = base_pressure + safety_margin + environment_adjustment
            pressure = total_pressure * altitude_correction

            # Corrected airflow (slightly less effect than pressure)
            flow_correction = 1 + (altitude / 120 / 100) if altitude > 0 else 1.0
            corrected_airflow = airflow * flow_correction

            power = (corrected_airflow * pressure) / (36000 * 0.5)

            return {
                'airflow_m3_min': corrected_airflow / 60,
                'airflow_m3_hr': corrected_airflow,
                'pressure_mbar': pressure,
                'power_kw': power,
                'breakdown': {
                    'base_airflow_m3_min': airflow / 60,
                    'base_airflow_m3_hr': airflow,
                    'corrected_airflow_m3_hr': corrected_airflow,
                    'static_pressure': kwargs.get('tank_depth', 2) * 100,
                    'pipe_friction': 15,
                    'fitting_losses': 10,
                    'diffuser_loss': 250,
                    'subtotal_pressure': base_pressure,
                    'safety_margin': safety_margin,
                    'environment_adjustment': environment_adjustment,
                    'total_pressure': total_pressure,
                    'final_pressure': pressure,
                    'pipe_velocity': 10,
                    'altitude_correction': altitude_correction,
                    'environment_factor': environment_factor,
                    'safety_factor': safety_factor,
                    'specific_gravity': 1.05
                },
                'tank_info': {
                    'area_m2': kwargs.get('tank_length', 6) * kwargs.get('tank_width', 3),
                    'volume_m3': kwargs.get('tank_length', 6) * kwargs.get('tank_width', 3) * kwargs.get('tank_depth', 2),
                    'depth_m': kwargs.get('tank_depth', 2),
                    'num_tanks': kwargs.get('num_tanks', 1),
                    'configuration': kwargs.get('tank_config', 'parallel')
                },
                'messages': ['Using fallback calculator' if not USING_ENHANCED else 'Using enhanced calculator'],
                'warnings': []
            }

# In-memory session storage (in production, use a database)
sessions = {}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # Parse request first
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self.send_error(400, "Invalid JSON")
            return

        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        # Get state from request (stateless operation)
        client_state = data.get('state', 'greeting')
        client_data = data.get('data', {})

        # Get or create session (fallback for development)
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'state': client_state,
                'data': client_data,
                'conversation': []
            }

        session = sessions[session_id]

        # Override with client state if provided (for stateless operation)
        if client_state:
            session['state'] = client_state
        if client_data:
            session['data'].update(client_data)

        response = {
            'session_id': session_id,
            'state': session['state'],
            'data': session['data']
        }

        # Add user message to conversation history
        session['conversation'].append({'role': 'user', 'message': message})

        # Handle conversation states
        # Special handling for initial message
        if message.lower() == 'start' or session['state'] == 'greeting':
            response['message'] = (
                "👋 Hi! I'm the Crelec Blower Selection Assistant.\\n\\n"
                "I'll help you find the perfect blower for your application. "
                "Let's start with some questions.\\n\\n"
                "**What type of operation do you need?**\\n\\n"
                "• **Compression** (blowing/aeration)\\n"
                "• **Vacuum** (suction/extraction)\\n\\n"
                "Please type 'compression' or 'vacuum':"
            )
            session['state'] = 'operation_type'
            response['state'] = 'operation_type'
            response['data'] = session['data']

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
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
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

        elif session['state'] == 'altitude':
            session['data']['altitude_text'] = message
            msg_lower = message.lower().strip()

            # Check for sea level or coastal first
            if 'sea' in msg_lower or 'coast' in msg_lower or msg_lower == '0':
                altitude = 0
            else:
                try:
                    # Try to extract a number from the message
                    numbers = re.findall(r'\d+', message)
                    altitude = float(numbers[0]) if numbers else 500
                except:
                    altitude = 500

            session['data']['altitude'] = altitude

            response['message'] = (
                f"✅ Location confirmed: {altitude}m altitude\\n\\n"
                "**Select your application:**\\n\\n"
                "1. **Waste Water** Treatment\\n"
                "2. **Fertiliser** Production\\n"
                "3. **Dental** Aspiration\\n"
                "4. **Sauna** Systems\\n"
                "5. **Aquaponics**/Fish Farming\\n"
                "6. **Bottling** Lines\\n"
                "7. **Pneumatic** Conveying\\n"
                "8. **Plastic** Mold Processing\\n"
                "9. **Metal** Treatment Baths\\n"
                "10. **Gas/Air** Circulation\\n"
                "11. **Materials** Handling\\n"
                "12. **Other** (please specify)\\n\\n"
                "Type a number (1-12) or application name:"
            )
            session['state'] = 'application'

        elif session['state'] == 'application':
            msg_lower = message.lower().strip()

            # Handle numbered inputs
            app_map = {
                '1': ('waste_water', 'Waste Water Treatment'),
                '2': ('fertiliser', 'Fertiliser Production'),
                '3': ('dental', 'Dental Aspiration'),
                '4': ('sauna', 'Sauna Systems'),
                '5': ('aquaponics', 'Aquaponics/Fish Farming'),
                '6': ('bottling', 'Bottling Lines'),
                '7': ('pneumatic', 'Pneumatic Conveying'),
                '8': ('plastic', 'Plastic Mold Processing'),
                '9': ('metal_treatment', 'Metal Treatment Baths'),
                '10': ('gas_circulation', 'Gas/Air Circulation'),
                '11': ('materials', 'Materials Handling'),
                '12': ('other', 'Other Application')
            }

            # Check if numeric input
            if message.strip() in app_map:
                session['data']['application'], app_msg = app_map[message.strip()]
            # Check text inputs
            elif 'waste' in msg_lower or 'water treat' in msg_lower:
                session['data']['application'] = 'waste_water'
                app_msg = "Waste Water Treatment"
            elif 'fertil' in msg_lower:
                session['data']['application'] = 'fertiliser'
                app_msg = "Fertiliser Production"
            elif 'dental' in msg_lower or 'aspir' in msg_lower:
                session['data']['application'] = 'dental'
                app_msg = "Dental Aspiration"
            elif 'sauna' in msg_lower:
                session['data']['application'] = 'sauna'
                app_msg = "Sauna Systems"
            elif 'fish' in msg_lower or 'aqua' in msg_lower or 'aquaponic' in msg_lower:
                session['data']['application'] = 'aquaponics'
                app_msg = "Aquaponics/Fish Farming"
            elif 'bottl' in msg_lower:
                session['data']['application'] = 'bottling'
                app_msg = "Bottling Lines"
            elif 'pneumatic' in msg_lower or 'convey' in msg_lower:
                session['data']['application'] = 'pneumatic'
                app_msg = "Pneumatic Conveying"
            elif 'plastic' in msg_lower or 'mold' in msg_lower or 'mould' in msg_lower:
                session['data']['application'] = 'plastic'
                app_msg = "Plastic Mold Processing"
            elif 'metal' in msg_lower or 'treatment' in msg_lower:
                session['data']['application'] = 'metal_treatment'
                app_msg = "Metal Treatment Baths"
            elif 'gas' in msg_lower or 'circulation' in msg_lower:
                session['data']['application'] = 'gas_circulation'
                app_msg = "Gas/Air Circulation"
            elif 'material' in msg_lower or 'handling' in msg_lower:
                session['data']['application'] = 'materials'
                app_msg = "Materials Handling"
            else:
                # Treat any other input as "Other" application
                session['data']['application'] = 'other'
                session['data']['application_detail'] = message
                app_msg = f"Other: {message}"

            response['message'] = (
                f"✅ {app_msg} selected.\\n\\n"
                "**Operating Environment:**\\n\\n"
                "What type of environment will the blower operate in?\\n\\n"
                "1. **Normal** - Standard indoor conditions\\n"
                "2. **Wet/Humid** - High moisture areas\\n"
                "3. **Dusty** - Particulate-laden air\\n"
                "4. **Coastal/Marine** - Salt air exposure\\n"
                "5. **Gas/Chemical** - Corrosive atmospheres\\n"
                "6. **Extreme Climate** - Very hot/cold conditions\\n\\n"
                "Type a number (1-6) or environment name:"
            )
            session['state'] = 'environment'

        elif session['state'] == 'environment':
            msg_lower = message.lower().strip()

            # Handle numbered inputs
            env_map = {
                '1': ('normal', 'Normal conditions', 1.0),
                '2': ('wet', 'Wet/Humid environment', 1.1),
                '3': ('dusty', 'Dusty environment', 1.15),
                '4': ('coastal', 'Coastal/Marine environment', 1.2),
                '5': ('gas', 'Gas/Chemical environment', 1.25),
                '6': ('climate', 'Extreme climate', 1.15)
            }

            # Check if numeric input
            if message.strip() in env_map:
                session['data']['environment'], env_msg, env_factor = env_map[message.strip()]
            # Process text environment selection
            elif 'normal' in msg_lower or 'standard' in msg_lower or 'indoor' in msg_lower:
                session['data']['environment'] = 'normal'
                env_msg = "Normal conditions"
                env_factor = 1.0
            elif 'wet' in msg_lower or 'humid' in msg_lower or 'moisture' in msg_lower:
                session['data']['environment'] = 'wet'
                env_msg = "Wet/Humid environment"
                env_factor = 1.1  # 10% safety increase
            elif 'dust' in msg_lower or 'particulate' in msg_lower:
                session['data']['environment'] = 'dusty'
                env_msg = "Dusty environment"
                env_factor = 1.15  # 15% safety increase
            elif 'coast' in msg_lower or 'marine' in msg_lower or 'salt' in msg_lower or 'sea' in msg_lower:
                session['data']['environment'] = 'coastal'
                env_msg = "Coastal/Marine environment"
                env_factor = 1.2  # 20% safety increase
            elif 'gas' in msg_lower or 'chemical' in msg_lower or 'corrosive' in msg_lower:
                session['data']['environment'] = 'gas'
                env_msg = "Gas/Chemical environment"
                env_factor = 1.25  # 25% safety increase
            elif 'extreme' in msg_lower or 'climate' in msg_lower or 'hot' in msg_lower or 'cold' in msg_lower:
                session['data']['environment'] = 'climate'
                env_msg = "Extreme climate"
                env_factor = 1.15  # 15% safety increase
            else:
                session['data']['environment'] = 'normal'
                env_msg = "Normal conditions (default)"
                env_factor = 1.0

            session['data']['environment_factor'] = env_factor

            response['message'] = (
                f"✅ {env_msg} selected.\\n\\n"
                "**TANK CONFIGURATION**\\n\\n"
                "How many tanks do you have? (1-10)\\n"
                "If you have multiple tanks, are they in 'series' or 'parallel'?\\n\\n"
                "Examples:\\n"
                "• '1' for single tank\\n"
                "• '3 parallel' for 3 tanks in parallel\\n"
                "• '2 series' for 2 tanks in series\\n\\n"
                "Number of tanks and configuration:"
            )
            session['state'] = 'tank_config'

        elif session['state'] == 'tank_config':
            # Parse tank configuration
            msg_lower = message.lower().strip()
            parts = msg_lower.split()

            try:
                # Extract number
                num_tanks = 1
                for part in parts:
                    if part.isdigit():
                        num_tanks = int(part)
                        break

                # Extract configuration
                if 'series' in msg_lower:
                    config = 'series'
                elif 'parallel' in msg_lower:
                    config = 'parallel'
                else:
                    config = 'parallel' if num_tanks > 1 else 'single'

                session['data']['num_tanks'] = num_tanks
                session['data']['tank_config'] = config

                config_msg = f"{num_tanks} tank{'s' if num_tanks > 1 else ''}"
                if num_tanks > 1:
                    config_msg += f" in {config}"

                response['message'] = (
                    f"✅ {config_msg} configured.\\n\\n"
                    "**TANK DIMENSIONS**\\n\\n"
                    "![Tank Dimensions](/assets/images/tank-dimensions.png)\\n\\n"
                    "Please provide tank size in meters:\\n"
                    "• **Format**: Length × Width × Depth\\n"
                    "• **Example**: 6 3 2 (or 6×3×2)\\n\\n"
                    "Tank dimensions:"
                )
                session['state'] = 'dimensions'

            except:
                response['message'] = (
                    "Please enter a number between 1-10, optionally followed by 'series' or 'parallel'\\n"
                    "Examples: '1', '3 parallel', '2 series'"
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return

        elif session['state'] == 'dimensions':
            try:
                parts = message.replace(',', ' ').replace('x', ' ').replace('×', ' ').split()
                if len(parts) >= 3:
                    length, width, height = map(float, parts[:3])
                    session['data']['length'] = length
                    session['data']['width'] = width
                    session['data']['height'] = height

                    response['message'] = (
                        f"✅ Tank: {length}m × {width}m × {height}m deep\\n\\n"
                        "**PIPE SYSTEM**\\n\\n"
                        "Please provide pipe details:\\n"
                        "• Diameter in mm (e.g., 50, 100, 150)\\n"
                        "• Length to tanks in meters\\n"
                        "• Number of 90° bends\\n\\n"
                        "Enter as: diameter length bends\\n"
                        "Example: '100 50 4'\\n"
                        "Or type 'default' to use standard values:\\n\\n"
                        "Pipe specifications:"
                    )
                    session['state'] = 'pipe_system'
                else:
                    response['message'] = "Please enter three numbers for length, width, and depth (in meters)"
            except:
                response['message'] = "Invalid format. Please enter: length width depth (e.g., '6 3 2')"

        elif session['state'] == 'pipe_system':
            msg_lower = message.lower().strip()

            if msg_lower == 'default':
                # Use default values based on application
                app = session['data'].get('application', 'industrial')
                if app == 'waste_water':
                    session['data']['pipe_diameter'] = 100
                    session['data']['pipe_length'] = 50
                    session['data']['num_bends'] = 4
                    pipe_msg = "100mm diameter, 50m length, 4 bends (default)"
                else:
                    session['data']['pipe_diameter'] = 50
                    session['data']['pipe_length'] = 30
                    session['data']['num_bends'] = 3
                    pipe_msg = "50mm diameter, 30m length, 3 bends (default)"
            else:
                try:
                    parts = message.split()
                    if len(parts) >= 3:
                        diameter = float(parts[0])
                        length = float(parts[1])
                        bends = int(parts[2])

                        # Validate ranges
                        if diameter < 25 or diameter > 500:
                            raise ValueError("Diameter must be 25-500mm")
                        if length < 1 or length > 1000:
                            raise ValueError("Length must be 1-1000m")
                        if bends < 0 or bends > 20:
                            raise ValueError("Bends must be 0-20")

                        session['data']['pipe_diameter'] = diameter
                        session['data']['pipe_length'] = length
                        session['data']['num_bends'] = bends
                        pipe_msg = f"{diameter}mm diameter, {length}m length, {bends} bends"
                    else:
                        raise ValueError("Need three values")
                except Exception as e:
                    response['message'] = (
                        f"Invalid input: {str(e)}\\n\\n"
                        "Please enter: diameter(mm) length(m) bends\\n"
                        "Example: '100 50 4'\\n"
                        "Or type 'default'"
                    )
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return

            response['message'] = (
                f"✅ Pipe system: {pipe_msg}\\n\\n"
                "**DIFFUSER TYPE**\\n\\n"
                "What type of diffuser system will you use?\\n\\n"
                "**1.** Fine bubble membrane (high efficiency)\\n"
                "**2.** Ceramic disc diffusers\\n"
                "**3.** Coarse bubble/perforated pipe\\n"
                "**4.** Tube diffusers\\n"
                "**5.** Other/custom system\\n\\n"
                "Please enter a number (1-5) or type the name:"
            )
            session['state'] = 'diffuser'

        elif session['state'] == 'diffuser':
            msg_lower = message.lower().strip()

            # Map numbers to diffuser types
            diffuser_map = {
                '1': 'fine',
                '2': 'disc',
                '3': 'coarse',
                '4': 'tube',
                '5': 'custom'
            }

            diffuser_types = {
                'fine': 'Fine bubble membrane',
                'disc': 'Ceramic disc',
                'coarse': 'Coarse bubble',
                'tube': 'Tube diffusers',
                'custom': 'Custom system'
            }

            # Check for numbered selection first
            selected_type = None
            if msg_lower in diffuser_map:
                selected_type = diffuser_map[msg_lower]
                selected_name = diffuser_types[selected_type]
            else:
                # Find matching type by name
                for key, name in diffuser_types.items():
                    if key in msg_lower:
                        selected_type = key
                        selected_name = name
                        break

                if not selected_type:
                    if 'membrane' in msg_lower:
                        selected_type = 'fine'
                        selected_name = 'Fine bubble membrane'
                    elif 'ceramic' in msg_lower:
                        selected_type = 'disc'
                        selected_name = 'Ceramic disc'
                    elif 'perforated' in msg_lower:
                        selected_type = 'coarse'
                        selected_name = 'Coarse bubble'
                    else:
                        selected_type = 'custom'
                        selected_name = 'Custom system'

            session['data']['diffuser_type'] = selected_type

            # Now calculate with all parameters
            calculator = EnhancedBlowerCalculator()

            result = calculator.calculate(
                tank_length=session['data']['length'],
                tank_width=session['data']['width'],
                tank_depth=session['data']['height'],
                num_tanks=session['data'].get('num_tanks', 1),
                tank_config=session['data'].get('tank_config', 'parallel'),
                application=session['data'].get('application', 'industrial'),
                altitude=session['data'].get('altitude', 0),
                pipe_diameter=session['data'].get('pipe_diameter'),
                pipe_length=session['data'].get('pipe_length'),
                num_bends=session['data'].get('num_bends'),
                diffuser_type=selected_type,
                environment_factor=session['data'].get('environment_factor', 1.0)
            )

            # Format the detailed response
            breakdown = result['breakdown']
            tank_info = result['tank_info']

            response['message'] = (
                f"✅ {selected_name} selected.\\n\\n"
                "═══════════════════════════════════════\\n"
                "📊 **CALCULATION RESULTS**\\n"
                "═══════════════════════════════════════\\n\\n"
                f"**Required Specifications:**\\n"
                f"• Airflow: **{result['airflow_m3_hr']:.1f} m³/hr** ({result['airflow_m3_min']:.3f} m³/min)\\n"
                f"• Pressure: **{result['pressure_mbar']:.0f} mbar**\\n"
                f"• Estimated Power: **{result['power_kw']:.1f} kW**\\n\\n"
                "**Calculation Breakdown:**\\n"
                "───────────────────────────\\n"
                f"Base Airflow: {breakdown['base_airflow_m3_hr']:.1f} m³/hr\\n"
                f"• Tank area: {tank_info['area_m2']:.1f} m² × factor\\n\\n"
                "**Pressure Components:**\\n"
                f"• Static head ({tank_info['depth_m']}m): {breakdown['static_pressure']:.0f} mbar\\n"
                f"• Pipe losses: {breakdown['pipe_friction']:.0f} mbar\\n"
                f"• Fitting losses: {breakdown['fitting_losses']:.0f} mbar\\n"
                f"• Diffuser loss: {breakdown['diffuser_loss']:.0f} mbar\\n"
                f"• Subtotal: {breakdown['subtotal_pressure']:.0f} mbar\\n"
                f"• Safety margin ({(breakdown['safety_factor']-1)*100:.0f}%): {breakdown['safety_margin']:.0f} mbar\\n"
            )

            # Add environment factor (always show it)
            env_factor = session['data'].get('environment_factor', 1.0)
            env_type = session['data'].get('environment', 'normal')
            env_adjustment_mbar = breakdown.get('environment_adjustment', 0)

            if env_factor > 1.0:
                env_increase = (env_factor - 1) * 100
                response['message'] += (
                    f"• Environment factor ({env_type}): +{env_increase:.0f}% ({env_adjustment_mbar:.0f} mbar)\\n"
                )
            else:
                response['message'] += (
                    f"• Environment factor ({env_type}): No adjustment (0 mbar)\\n"
                )

            # Add altitude correction if applicable
            altitude = session['data'].get('altitude', 0)
            if altitude > 0:
                altitude_increase = (breakdown['altitude_correction'] - 1) * 100
                response['message'] += (
                    f"• Altitude correction ({altitude}m): +{altitude_increase:.1f}%\\n"
                )

            response['message'] += (
                "───────────────────────────\\n"
                f"**Total Required: {breakdown['final_pressure']:.0f} mbar**\\n"
            )

            # Add messages and warnings
            if result['messages']:
                response['message'] += "\\n**Notes:**\\n"
                for msg in result['messages']:
                    response['message'] += f"• {msg}\\n"

            if result['warnings']:
                response['message'] += "\\n⚠️ **Warnings:**\\n"
                for warn in result['warnings']:
                    response['message'] += f"• {warn}\\n"

            response['message'] += (
                "\\n═══════════════════════════════════════\\n\\n"
                "Would you like to:\\n"
                "• Get a **quote** with recommended products\\n"
                "• **Recalculate** with different parameters\\n"
                "• View **energy savings** with multiple blowers\\n\\n"
                "Type 'quote', 'recalculate', or 'energy':"
            )

            # Store results for quote generation
            session['data']['results'] = result
            session['state'] = 'results'

        elif session['state'] == 'results':
            msg_lower = message.lower().strip()

            if 'quote' in msg_lower:
                response['message'] = (
                    "📧 To receive your detailed quote, please enter your email address:\\n\\n"
                    "We'll send you:\\n"
                    "• Professional PDF quote\\n"
                    "• Recommended blower models\\n"
                    "• Technical specifications\\n"
                    "• Pricing information\\n\\n"
                    "Email address:"
                )
                session['state'] = 'email'

            elif 'recalc' in msg_lower or 'again' in msg_lower:
                # Reset session but keep some data
                sessions[session_id] = {
                    'state': 'greeting',
                    'data': {},
                    'conversation': []
                }
                response['message'] = (
                    "Let's start over!\\n\\n"
                    "**What type of operation do you need?**\\n\\n"
                    "• **Compression** (blowing/aeration)\\n"
                    "• **Vacuum** (suction/extraction)\\n\\n"
                    "Please type 'compression' or 'vacuum':"
                )
                session['state'] = 'operation_type'

            elif 'energy' in msg_lower:
                # Show energy optimization comparison
                response['message'] = (
                    "⚡ **Energy Optimization Analysis**\\n"
                    "═══════════════════════════════════════\\n\\n"
                    "**Single Blower Configuration:**\\n"
                    f"• Power required: {session['data']['results']['power_kw']:.1f} kW\\n"
                    f"• Annual energy: {session['data']['results']['power_kw'] * 8760:.0f} kWh/year\\n"
                    f"• Annual cost: R{session['data']['results']['power_kw'] * 8760 * 2:.0f}\\n\\n"
                    "**Multiple Blower Benefits:**\\n"
                    "• 2 blowers at 70% speed = 69% power\\n"
                    "• 3 blowers at 60% speed = 43% power\\n"
                    "• Potential savings: 30-50%\\n"
                    "• Better turndown capability\\n"
                    "• Redundancy for maintenance\\n\\n"
                    "Would you like a quote? Type 'quote':"
                )
            else:
                response['message'] = "Please type 'quote', 'recalculate', or 'energy':"

        elif session['state'] == 'email':
            # Email validation
            if '@' in message and '.' in message:
                session['data']['email'] = message

                # Generate quote ID
                import datetime
                quote_id = f"Q{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

                # Prepare email data for frontend
                email_data = {
                    'quote_id': quote_id,
                    'customer_data': {
                        'email': message,
                        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                        'time': datetime.datetime.now().strftime('%H:%M')
                    },
                    'calculation': {
                        'results': session['data'].get('results', {}),
                        'tank_dimensions': f"{session['data'].get('length', 0)}m × {session['data'].get('width', 0)}m × {session['data'].get('height', 0)}m",
                        'application': session['data'].get('application', 'industrial'),
                        'altitude': session['data'].get('altitude', 0),
                        'num_tanks': session['data'].get('num_tanks', 1),
                        'tank_config': session['data'].get('tank_config', 'single')
                    },
                    'products': []  # Would normally fetch from product database
                }

                # Add flags to trigger frontend email handling
                response['send_email'] = True
                response['email_data'] = email_data
                response['message'] = (
                    "✅ Thank you! Your quote is being generated...\\n\\n"
                    "You'll receive:\\n"
                    "• Detailed PDF quote\\n"
                    "• Product recommendations\\n"
                    "• Technical specifications\\n\\n"
                    "A Crelec representative will contact you soon.\\n\\n"
                    "Type 'restart' for a new calculation."
                )
                session['state'] = 'complete'
            else:
                response['message'] = "Please enter a valid email address (e.g., name@company.com):"

        elif session['state'] == 'complete':
            if 'restart' in message.lower():
                sessions[session_id] = {
                    'state': 'greeting',
                    'data': {},
                    'conversation': []
                }
                response['message'] = (
                    "Starting new calculation...\\n\\n"
                    "**What type of operation do you need?**\\n\\n"
                    "• **Compression** (blowing/aeration)\\n"
                    "• **Vacuum** (suction/extraction)\\n\\n"
                    "Please type 'compression' or 'vacuum':"
                )
                session['state'] = 'operation_type'
            else:
                response['message'] = "Thank you for using Crelec Blower Selection. Type 'restart' for a new calculation."

        # Update response with latest state and data before sending
        response['state'] = session['state']
        response['data'] = session['data']

        # Send response with CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())