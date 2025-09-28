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
        response['message'] = (
            "Hi! I'll help you select the right blower for your needs.\n\n"
            "First, what type of operation do you need?\n\n"
            "1️⃣ **Compression** (Blowing air into tanks, aeration)\n"
            "2️⃣ **Vacuum** (Suction, extraction, conveying)\n\n"
            "Please type 1 for Compression or 2 for Vacuum:"
        )
        chat_state.update_session(message.session_id, 'operation_type', {})

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
        chat_state.update_session(message.session_id, 'dimensions', {'operation_type': operation})

        response['message'] = (
            f"✅ {operation_display} selected.\n\n"
            "Now, let's size your system. "
            "Please enter your tank dimensions in meters (length width height):\n"
            "For example: '6 3 2'"
        )

    elif current_state == 'dimensions':
        # Parse dimensions
        try:
            parts = message.message.replace(',', ' ').split()
            if len(parts) >= 3:
                length, width, height = map(float, parts[:3])
                data = {'length': length, 'width': width, 'height': height}
                chat_state.update_session(message.session_id, 'altitude', data)
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
        # Parse altitude or location
        try:
            # Try to parse as number first
            altitude = float(message.message.split()[0])
            session['data']['altitude'] = altitude
            chat_state.update_session(message.session_id, 'application', {})
            response['message'] = (
                f"Altitude set to {altitude}m above sea level.\n"
                "What's your application? Choose one:\n"
                "1. Waste Water Treatment\n"
                "2. Fish Hatchery\n"
                "3. General Industrial"
            )
        except ValueError:
            # TODO: Implement location to altitude lookup
            # For now, use a default
            session['data']['altitude'] = 500
            chat_state.update_session(message.session_id, 'application', {'altitude': 500})
            response['message'] = (
                f"I'll use 500m as the altitude for now.\n"
                "What's your application? Choose one:\n"
                "1. Waste Water Treatment\n"
                "2. Fish Hatchery\n"
                "3. General Industrial"
            )

    elif current_state == 'application':
        # Determine application type
        if '1' in user_msg or 'waste' in user_msg:
            app_type = 'waste_water'
        elif '2' in user_msg or 'fish' in user_msg:
            app_type = 'fish_hatchery'
        else:
            app_type = 'general'

        session['data']['application_type'] = app_type
        chat_state.update_session(message.session_id, 'calculating', {})

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