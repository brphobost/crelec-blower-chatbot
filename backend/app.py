"""
FastAPI Backend for Blower Selection Chatbot
Handles chat conversations, calculations, and quote generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import sqlite3
import uuid
from pathlib import Path

from calculator import BlowerCalculator, CalculationInput

app = FastAPI(title="Crelec Blower Selection API")

# Enable CORS for web widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize calculator
calculator = BlowerCalculator()

# Database setup
DB_PATH = Path("blower_quotes.db")


class ChatMessage(BaseModel):
    """Chat message model"""
    session_id: str
    message: str
    context: Optional[Dict] = {}


class CalculationRequest(BaseModel):
    """Calculation request model"""
    length: float
    width: float
    height: float
    altitude: float
    application_type: Optional[str] = "waste_water"
    safety_factor: Optional[float] = 1.2
    email: Optional[str] = None


class ChatState:
    """Manages chat conversation state"""

    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'state': 'welcome',
                'data': {},
                'messages': []
            }
        return self.sessions[session_id]

    def update_session(self, session_id: str, state: str, data: Dict):
        session = self.get_session(session_id)
        session['state'] = state
        session['data'].update(data)
        return session


# Initialize chat state manager
chat_state = ChatState()


def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            messages TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    # Quotes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            customer_email TEXT,
            calculation_input TEXT,
            calculation_result TEXT,
            recommended_products TEXT,
            created_at TIMESTAMP,
            status TEXT DEFAULT 'draft'
        )
    """)

    conn.commit()
    conn.close()


# Initialize database on startup
init_db()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Crelec Blower Selection API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.post("/api/chat")
async def chat(message: ChatMessage):
    """
    Handle chat conversation
    Progressive data collection for blower selection
    """
    session = chat_state.get_session(message.session_id)
    user_msg = message.message.lower().strip()
    response = {"session_id": message.session_id}

    current_state = session['state']

    # State machine for conversation flow
    if current_state == 'welcome':
        # Send welcome message - this should trigger automatically when chat starts
        # The frontend should handle this initial state
        chat_state.update_session(message.session_id, 'operation_type', {})
        response['message'] = (
            "Welcome! Let's select the right blower for your needs.\n\n"
            "First, what type of operation do you need?\n\n"
            "1️⃣ **Compression** (Blowing air into tanks, aeration)\n"
            "2️⃣ **Vacuum** (Suction, extraction, conveying)\n\n"
            "Please type 1 for Compression or 2 for Vacuum:"
        )

    elif current_state == 'operation_type':
        # Parse operation type selection
        user_msg_lower = message.message.lower().strip()

        if '1' in user_msg or 'compression' in user_msg_lower or 'blowing' in user_msg_lower or 'aeration' in user_msg_lower:
            operation = 'compression'
            operation_display = 'Compression/Blowing'
        elif '2' in user_msg or 'vacuum' in user_msg_lower or 'suction' in user_msg_lower:
            operation = 'vacuum'
            operation_display = 'Vacuum/Suction'
        else:
            response['message'] = (
                "Please select the operation type:\n"
                "1 - Compression (for aeration, blowing)\n"
                "2 - Vacuum (for suction, extraction)"
            )
            return response

        session['data']['operation_type'] = operation
        chat_state.update_session(message.session_id, 'installation', {'operation_type': operation})

        response['message'] = (
            f"✅ {operation_display} selected.\n\n"
            "Who will be handling the installation?\n\n"
            "1️⃣ **Self** (DIY installation)\n"
            "2️⃣ **Consultant/Contractor** (Professional installation)\n\n"
            "Please type 1 or 2:"
        )

    elif current_state == 'installation':
        # Parse installation type
        user_msg_lower = message.message.lower().strip()

        if '1' in user_msg or 'self' in user_msg_lower or 'diy' in user_msg_lower:
            installation = 'self'
            install_display = 'Self-installation'
        elif '2' in user_msg or 'consultant' in user_msg_lower or 'contractor' in user_msg_lower or 'professional' in user_msg_lower:
            installation = 'consultant'
            install_display = 'Professional installation'
        else:
            response['message'] = (
                "Please select installation type:\n"
                "1 - Self installation\n"
                "2 - Consultant/Contractor"
            )
            return response

        session['data']['installation'] = installation
        chat_state.update_session(message.session_id, 'altitude', {'installation': installation})

        response['message'] = (
            f"✅ {install_display} noted.\n\n"
            "What's the altitude of your installation site?\n"
            "You can provide:\n"
            "• Altitude in meters (e.g., '1420m')\n"
            "• City name (e.g., 'Johannesburg')\n"
            "• 'Sea level' or 'coastal'\n\n"
            "Location or altitude:"
        )


    elif current_state == 'altitude':
        # Parse altitude or location using location handler
        from location_handler import LocationHandler

        handler = LocationHandler()
        location_data = handler.process_location_input(message.message)

        session['data']['altitude'] = location_data.altitude
        session['data']['temperature'] = location_data.temperature
        session['data']['location'] = location_data.city if location_data.city else message.message

        chat_state.update_session(message.session_id, 'application', {
            'altitude': location_data.altitude,
            'temperature': location_data.temperature
        })

        # Build response with location info
        altitude_msg = f"✅ Location confirmed: {location_data.altitude}m altitude"
        if location_data.city:
            altitude_msg += f" ({location_data.city.title()})"

        response['message'] = (
            f"{altitude_msg}\n\n"
            "What's your application?\n\n"
            "1️⃣ **Waste Water Treatment** (aeration tanks)\n"
            "2️⃣ **Fish Farming/Aquaculture**\n"
            "3️⃣ **Industrial Process** (general)\n"
            "4️⃣ **Other** (describe)\n\n"
            "Please select 1-4:"
        )

    elif current_state == 'application':
        # Determine application type
        if '1' in user_msg or 'waste' in user_msg:
            app_type = 'waste_water'
            app_display = 'Waste Water Treatment'
        elif '2' in user_msg or 'fish' in user_msg:
            app_type = 'fish_hatchery'
            app_display = 'Fish Farming/Aquaculture'
        elif '3' in user_msg or 'industrial' in user_msg:
            app_type = 'industrial'
            app_display = 'Industrial Process'
        else:
            app_type = 'other'
            app_display = 'Other Application'

        session['data']['application_type'] = app_type
        chat_state.update_session(message.session_id, 'dimensions', {'application_type': app_type})

        response['message'] = (
            f"✅ {app_display} selected.\n\n"
            "**OPERATIONAL DATA**\n\n"
            "Let's start with your tank/system dimensions.\n"
            "Please provide tank size in meters:\n\n"
            "• Length × Width × Depth (e.g., '6 3 2')\n"
            "• Or total volume in m³ (e.g., '36')\n\n"
            "Tank dimensions:"
        )
        return response

    elif current_state == 'dimensions':
        # Now parse the actual dimensions after application
        try:
            parts = message.message.replace(',', ' ').replace('x', ' ').replace('×', ' ').split()
            if len(parts) >= 3:
                length, width, height = map(float, parts[:3])
                data = {'length': length, 'width': width, 'height': height}
                chat_state.update_session(message.session_id, 'num_tanks', data)
                volume = length * width * height
                response['message'] = (
                    f"✅ Tank: {length}m × {width}m × {height}m = {volume:.0f}m³\n\n"
                    "How many tanks do you have?\n"
                    "(Enter number, e.g., '1' or '3'):"
                )
            elif len(parts) == 1:
                # Direct volume entry
                volume = float(parts[0])
                # Estimate dimensions
                side = (volume ** (1/3))
                data = {
                    'length': side * 1.5,
                    'width': side,
                    'height': side * 0.67,
                    'volume': volume
                }
                chat_state.update_session(message.session_id, 'num_tanks', data)
                response['message'] = (
                    f"✅ Tank volume: {volume}m³\n\n"
                    "How many tanks do you have?\n"
                    "(Enter number, e.g., '1' or '3'):"
                )
            else:
                response['message'] = (
                    "Please enter dimensions as:\n"
                    "• Length Width Depth (e.g., '6 3 2')\n"
                    "• Or total volume (e.g., '36')"
                )
        except ValueError:
            response['message'] = (
                "I couldn't understand those dimensions.\n"
                "Please enter as 'Length Width Depth' (e.g., '6 3 2')"
            )
        return response

    elif current_state == 'num_tanks':
        # Parse number of tanks
        try:
            num_tanks = int(message.message.strip())
            session['data']['num_tanks'] = num_tanks
            chat_state.update_session(message.session_id, 'pipe_details', {'num_tanks': num_tanks})

            total_volume = session['data'].get('volume',
                session['data']['length'] * session['data']['width'] * session['data']['height']) * num_tanks

            response['message'] = (
                f"✅ {num_tanks} tank(s), total volume: {total_volume:.0f}m³\n\n"
                "**PIPING DETAILS**\n\n"
                "What's the pipe diameter to your tanks? (mm)\n"
                "Common sizes: 40mm, 50mm, 100mm, 150mm\n\n"
                "Pipe diameter:"
            )
        except ValueError:
            response['message'] = "Please enter the number of tanks (e.g., '1' or '3'):"
        return response

    elif current_state == 'pipe_details':
        # Parse pipe diameter
        try:
            pipe_dia = float(message.message.replace('mm', '').strip())
            session['data']['pipe_diameter'] = pipe_dia
            chat_state.update_session(message.session_id, 'calculating', {'pipe_diameter': pipe_dia})

            # Skip detailed pipe questions for now and calculate
            session['data']['pipe_length'] = 50  # Default
            session['data']['num_bends'] = 4  # Default

            # Trigger calculation
            chat_state.update_session(message.session_id, 'calculating', {})
            # Fall through to calculating state
        except ValueError:
            response['message'] = "Please enter pipe diameter in mm (e.g., '100' or '150mm'):"
            return response

    elif current_state == 'calculating':
        # Perform calculation
        calc_result = calculator.calculate_from_form_data(session['data'])

        if calc_result['success']:
            # Save quote to database
            quote_id = save_quote(
                session_id=message.session_id,
                calculation_input=session['data'],
                calculation_result=calc_result
            )

            # Get product recommendations
            products = get_product_recommendations(calc_result['results'])

            response['message'] = format_results(calc_result, products, quote_id)
            response['calculation'] = calc_result
            response['products'] = products
            response['quote_id'] = quote_id

            # Reset for new calculation
            chat_state.update_session(message.session_id, 'complete', {'quote_id': quote_id})
        else:
            response['message'] = f"Error in calculation: {calc_result['error']}"
            chat_state.update_session(message.session_id, 'welcome', {})

    elif current_state == 'complete':
        response['message'] = (
            "Would you like to:\n"
            "1. Start a new calculation (type 'new')\n"
            "2. Adjust the previous calculation (type 'adjust')\n"
            "3. Get help from a human expert (type 'help')"
        )
        if 'new' in user_msg:
            chat_state.update_session(message.session_id, 'welcome', {})
            response['message'] = (
                "Starting a new calculation. "
                "Please enter your tank dimensions in meters (length width height):"
            )

    # Store message in session
    session['messages'].append({
        'user': message.message,
        'bot': response['message'],
        'timestamp': datetime.now().isoformat()
    })

    return response


@app.post("/api/calculate")
async def calculate(request: CalculationRequest):
    """
    Direct calculation endpoint
    """
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

        quote_id = save_quote(
            session_id=str(uuid.uuid4()),
            calculation_input=request.dict(),
            calculation_result={
                'airflow_required': result.airflow_required,
                'pressure_required': result.pressure_required,
                'power_estimate': result.power_estimate,
                'tank_volume': result.tank_volume,
                'notes': result.notes
            }
        )

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
    """
    Match products based on requirements
    TODO: Load from actual product database
    """
    airflow = requirements['airflow_required']
    pressure = requirements['pressure_required']

    # Mock product database
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

    # Simple matching algorithm
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

    # Sort by match score
    matched.sort(key=lambda x: x['match_score'], reverse=True)

    # Return top 3
    return matched[:3]


def format_results(calc_result: Dict, products: List[Dict], quote_id: str) -> str:
    """Format calculation results for chat response"""
    results = calc_result['results']

    message = f"""
✅ **Calculation Complete!** Quote ID: {quote_id}

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


def save_quote(session_id: str, calculation_input: Dict, calculation_result: Dict) -> str:
    """Save quote to database"""
    quote_id = f"Q{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO quotes (id, conversation_id, calculation_input, calculation_result, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        quote_id,
        session_id,
        json.dumps(calculation_input),
        json.dumps(calculation_result),
        datetime.now()
    ))

    conn.commit()
    conn.close()

    return quote_id


@app.get("/api/quote/{quote_id}")
async def get_quote(quote_id: str):
    """Retrieve a quote by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM quotes WHERE id = ?",
        (quote_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'quote_id': row[0],
            'calculation_input': json.loads(row[3]),
            'calculation_result': json.loads(row[4]),
            'created_at': row[6]
        }
    else:
        raise HTTPException(status_code=404, detail="Quote not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)