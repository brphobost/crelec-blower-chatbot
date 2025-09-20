"""
Vercel Serverless Function Entry Point
This wraps our FastAPI app for Vercel deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import json
import uuid
import math

# Calculator classes embedded directly for Vercel
@dataclass
class CalculationInput:
    """Input parameters for blower calculation"""
    length: float
    width: float
    height: float
    altitude: float
    application_type: str = "waste_water"
    safety_factor: float = 1.2
    air_changes_per_hour: Optional[float] = None

@dataclass
class CalculationResult:
    """Result of blower calculation"""
    airflow_required: float
    pressure_required: float
    power_estimate: float
    tank_volume: float
    notes: list

class BlowerCalculator:
    """Simple calculator for blower selection"""

    AIR_CHANGES_DEFAULT = {
        "waste_water": 6,
        "fish_hatchery": 10,
        "general": 4
    }

    def calculate_basic(self, input_data: CalculationInput) -> CalculationResult:
        tank_volume = input_data.length * input_data.width * input_data.height

        if input_data.air_changes_per_hour:
            air_changes = input_data.air_changes_per_hour
        else:
            air_changes = self.AIR_CHANGES_DEFAULT.get(
                input_data.application_type,
                self.AIR_CHANGES_DEFAULT["general"]
            )

        airflow_base = tank_volume * air_changes
        airflow_required = airflow_base * input_data.safety_factor

        pressure_required = self._calculate_pressure(
            input_data.height,
            input_data.altitude
        )

        power_estimate = self._estimate_power(airflow_required, pressure_required)

        notes = [
            f"Tank volume: {tank_volume:.1f} m³",
            f"Air changes per hour: {air_changes}",
            f"Safety factor applied: {input_data.safety_factor}",
            f"Altitude adjustment: {input_data.altitude}m above sea level"
        ]

        return CalculationResult(
            airflow_required=round(airflow_required, 1),
            pressure_required=round(pressure_required, 1),
            power_estimate=round(power_estimate, 2),
            tank_volume=round(tank_volume, 1),
            notes=notes
        )

    def _calculate_pressure(self, depth: float, altitude: float) -> float:
        water_pressure = depth * 98.1
        system_losses = 150
        altitude_correction = (altitude / 100) * 12
        total_pressure = water_pressure + system_losses + altitude_correction
        return total_pressure

    def _estimate_power(self, airflow: float, pressure: float) -> float:
        airflow_m3_s = airflow / 3600
        pressure_pa = pressure * 100
        theoretical_power = airflow_m3_s * pressure_pa
        efficiency = 0.6
        actual_power = theoretical_power / efficiency
        power_kw = actual_power / 1000
        return power_kw

    def calculate_from_form_data(self, form_data: Dict) -> Dict:
        try:
            calc_input = CalculationInput(
                length=float(form_data.get('length', 0)),
                width=float(form_data.get('width', 0)),
                height=float(form_data.get('height', 0)),
                altitude=float(form_data.get('altitude', 0)),
                application_type=form_data.get('application_type', 'waste_water'),
                safety_factor=float(form_data.get('safety_factor', 1.2))
            )

            result = self.calculate_basic(calc_input)

            return {
                'success': True,
                'input': {
                    'dimensions': f"{calc_input.length}x{calc_input.width}x{calc_input.height}m",
                    'altitude': f"{calc_input.altitude}m",
                    'application': calc_input.application_type
                },
                'results': {
                    'airflow_required': result.airflow_required,
                    'pressure_required': result.pressure_required,
                    'power_estimate': result.power_estimate,
                    'tank_volume': result.tank_volume,
                    'units': {
                        'airflow': 'm³/hr',
                        'pressure': 'mbar',
                        'power': 'kW',
                        'volume': 'm³'
                    }
                },
                'notes': result.notes
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

app = FastAPI(title="Crelec Blower Selection API")

# Enable CORS for web widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize calculator
calculator = BlowerCalculator()

class ChatMessage(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict] = {}

class CalculationRequest(BaseModel):
    length: float
    width: float
    height: float
    altitude: float
    application_type: Optional[str] = "waste_water"
    safety_factor: Optional[float] = 1.2
    email: Optional[str] = None

# In-memory storage for serverless (use Supabase for persistence)
sessions = {}

@app.get("/api")
async def root():
    return {
        "name": "Crelec Blower Selection API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    session_id = message.session_id

    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = {
            'state': 'welcome',
            'data': {},
            'messages': []
        }

    session = sessions[session_id]
    user_msg = message.message.lower().strip()
    response = {"session_id": session_id}

    current_state = session['state']

    # State machine for conversation flow
    if current_state == 'welcome':
        response['message'] = (
            "Hi! I'll help you select the right blower for your needs. "
            "Let's start with your tank dimensions. "
            "Please enter the length, width, and height in meters (e.g., '6 3 2'):"
        )
        session['state'] = 'dimensions'

    elif current_state == 'dimensions':
        try:
            parts = message.message.replace(',', ' ').split()
            if len(parts) >= 3:
                length, width, height = map(float, parts[:3])
                session['data'] = {'length': length, 'width': width, 'height': height}
                session['state'] = 'altitude'
                response['message'] = (
                    f"Got it! Tank dimensions: {length}m × {width}m × {height}m\n"
                    "Now, what's your facility's altitude above sea level in meters? "
                    "(Or tell me your city/location and I'll look it up)"
                )
            else:
                response['message'] = (
                    "I need three numbers for length, width, and height. "
                    "Please enter them separated by spaces (e.g., '6 3 2'):"
                )
        except ValueError:
            response['message'] = (
                "I couldn't understand those dimensions. "
                "Please enter three numbers in meters (e.g., '6 3 2'):"
            )

    elif current_state == 'altitude':
        try:
            altitude = float(message.message.split()[0])
            session['data']['altitude'] = altitude
            session['state'] = 'application'
            response['message'] = (
                f"Altitude set to {altitude}m above sea level.\n"
                "What's your application? Choose one:\n"
                "1. Waste Water Treatment\n"
                "2. Fish Hatchery\n"
                "3. General Industrial"
            )
        except ValueError:
            session['data']['altitude'] = 500
            session['state'] = 'application'
            response['message'] = (
                f"I'll use 500m as the altitude for now.\n"
                "What's your application? Choose one:\n"
                "1. Waste Water Treatment\n"
                "2. Fish Hatchery\n"
                "3. General Industrial"
            )

    elif current_state == 'application':
        if '1' in user_msg or 'waste' in user_msg:
            app_type = 'waste_water'
        elif '2' in user_msg or 'fish' in user_msg:
            app_type = 'fish_hatchery'
        else:
            app_type = 'general'

        session['data']['application_type'] = app_type
        session['state'] = 'calculating'

        # Perform calculation
        calc_result = calculator.calculate_from_form_data(session['data'])

        if calc_result['success']:
            quote_id = f"Q{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            products = get_product_recommendations(calc_result['results'])

            response['message'] = format_results(calc_result, products, quote_id)
            response['calculation'] = calc_result
            response['products'] = products
            response['quote_id'] = quote_id

            session['state'] = 'complete'
        else:
            response['message'] = f"Error in calculation: {calc_result['error']}"
            session['state'] = 'welcome'

    elif current_state == 'complete':
        response['message'] = (
            "Would you like to:\n"
            "1. Start a new calculation (type 'new')\n"
            "2. Adjust the previous calculation (type 'adjust')\n"
            "3. Get help from a human expert (type 'help')"
        )
        if 'new' in user_msg:
            session['state'] = 'welcome'
            session['data'] = {}
            response['message'] = (
                "Starting a new calculation. "
                "Please enter your tank dimensions in meters (length width height):"
            )

    # Store message
    session['messages'].append({
        'user': message.message,
        'bot': response['message'],
        'timestamp': datetime.now().isoformat()
    })

    return response

@app.post("/api/calculate")
async def calculate(request: CalculationRequest):
    try:
        calc_input = CalculationInput(
            length=request.length,
            width=request.width,
            height=request.height,
            altitude=request.altitude,
            application_type=request.application_type,
            safety_factor=request.safety_factor
        )

        result = calculator.calculate_basic(calc_input)
        products = get_product_recommendations({
            'airflow_required': result.airflow_required,
            'pressure_required': result.pressure_required
        })

        quote_id = f"Q{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        return {
            'success': True,
            'quote_id': quote_id,
            'results': {
                'airflow_required': result.airflow_required,
                'pressure_required': result.pressure_required,
                'power_estimate': result.power_estimate,
                'tank_volume': result.tank_volume
            },
            'products': products,
            'notes': result.notes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_product_recommendations(requirements: Dict) -> List[Dict]:
    airflow = requirements['airflow_required']
    pressure = requirements['pressure_required']

    products = [
        {
            'model': 'Griffin GIS 36 2RB',
            'airflow_range': [500, 800],
            'pressure_range': [300, 500],
            'power': 5.5,
            'price': 'R45,000',
            'stock': 'In Stock'
        },
        {
            'model': 'Griffin G20 36 2RB',
            'airflow_range': [400, 700],
            'pressure_range': [250, 450],
            'power': 4.0,
            'price': 'R38,000',
            'stock': 'In Stock'
        },
        {
            'model': 'HB5515',
            'airflow_range': [600, 900],
            'pressure_range': [350, 550],
            'power': 7.5,
            'price': 'R52,000',
            'stock': '2 weeks delivery'
        },
        {
            'model': 'HB8520',
            'airflow_range': [800, 1200],
            'pressure_range': [400, 600],
            'power': 11.0,
            'price': 'R68,000',
            'stock': 'In Stock'
        }
    ]

    matched = []
    for product in products:
        if (product['airflow_range'][0] <= airflow <= product['airflow_range'][1] and
                product['pressure_range'][0] <= pressure <= product['pressure_range'][1]):
            product['match_score'] = 100
            matched.append(product)
        elif (airflow <= product['airflow_range'][1] * 1.2 and
              pressure <= product['pressure_range'][1] * 1.2):
            product['match_score'] = 80
            matched.append(product)

    matched.sort(key=lambda x: x['match_score'], reverse=True)
    return matched[:3]

def format_results(calc_result: Dict, products: List[Dict], quote_id: str) -> str:
    results = calc_result['results']

    message = f"""✅ **Calculation Complete!** Quote ID: {quote_id}

**Your Requirements:**
- Airflow: {results['airflow_required']} m³/hr
- Pressure: {results['pressure_required']} mbar
- Estimated Power: {results['power_estimate']} kW

**Recommended Blowers:**
"""

    for i, product in enumerate(products, 1):
        message += f"""
{i}. **{product['model']}**
   - Power: {product['power']} kW
   - Price: {product['price']}
   - Status: {product['stock']}
"""

    message += "\n📧 Would you like me to email you this quote? (Please provide your email)"

    return message

# This is the key part for Vercel
app = app