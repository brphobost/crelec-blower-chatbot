"""
Improved Chat Flow for Blower Selection
========================================
User-friendly conversational flow that guides users through
the selection process with context and smart defaults.

Author: Liberlocus for Crelec S.A.
Date: September 2025
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from comprehensive_calculator import (
    ComprehensiveBlowerCalculator,
    CalculationInputs,
    CalculationResults
)


class ChatState(Enum):
    """Chat conversation states"""
    WELCOME = "welcome"
    OPERATION_TYPE = "operation_type"
    APPLICATION = "application"
    LOCATION = "location"
    TANK_SIZE = "tank_size"
    TANK_DETAILS = "tank_details"
    LOAD_PATTERN = "load_pattern"
    CALCULATING = "calculating"
    RESULTS = "results"
    QUOTE = "quote"
    COMPLETE = "complete"


@dataclass
class UserSession:
    """User session data"""
    session_id: str
    state: ChatState = ChatState.WELCOME
    data: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict] = field(default_factory=list)
    calculation_results: Optional[CalculationResults] = None

    # Track what's been collected
    has_application: bool = False
    has_location: bool = False
    has_tank_size: bool = False
    has_load_pattern: bool = False


class ImprovedChatFlow:
    """
    Manages the conversational flow for blower selection
    with improved UX and smart defaults
    """

    def __init__(self):
        self.calculator = ComprehensiveBlowerCalculator()
        self.sessions: Dict[str, UserSession] = {}

        # Quick options for common scenarios
        self.quick_applications = {
            '1': 'waste_water',
            '2': 'fish_hatchery',
            '3': 'industrial',
            'waste': 'waste_water',
            'fish': 'fish_hatchery',
            'industrial': 'industrial',
            'sewage': 'waste_water',
            'aquaculture': 'fish_hatchery',
            'manufacturing': 'industrial'
        }

        # Common tank sizes
        self.typical_tanks = {
            'small': {'length': 4, 'width': 2, 'depth': 2, 'volume': 16},
            'medium': {'length': 6, 'width': 3, 'depth': 2.5, 'volume': 45},
            'large': {'length': 10, 'width': 5, 'depth': 3, 'volume': 150},
            'xlarge': {'length': 15, 'width': 8, 'depth': 4, 'volume': 480}
        }

    def get_session(self, session_id: str) -> UserSession:
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = UserSession(session_id=session_id)
        return self.sessions[session_id]

    def process_message(self, session_id: str, user_input: str) -> Dict:
        """
        Process user message and return response
        """
        session = self.get_session(session_id)
        user_input_lower = user_input.lower().strip()

        # Store message
        session.messages.append({
            'user': user_input,
            'state': session.state.value
        })

        # Route to appropriate handler
        handlers = {
            ChatState.WELCOME: self._handle_welcome,
            ChatState.OPERATION_TYPE: self._handle_operation_type,
            ChatState.APPLICATION: self._handle_application,
            ChatState.LOCATION: self._handle_location,
            ChatState.TANK_SIZE: self._handle_tank_size,
            ChatState.TANK_DETAILS: self._handle_tank_details,
            ChatState.LOAD_PATTERN: self._handle_load_pattern,
            ChatState.CALCULATING: self._handle_calculating,
            ChatState.RESULTS: self._handle_results,
            ChatState.QUOTE: self._handle_quote
        }

        handler = handlers.get(session.state, self._handle_welcome)
        response = handler(session, user_input)

        # Store bot response
        session.messages.append({
            'bot': response['message'],
            'state': session.state.value
        })

        return response

    def _handle_welcome(self, session: UserSession, user_input: str) -> Dict:
        """Handle welcome state"""
        session.state = ChatState.OPERATION_TYPE

        return {
            'message': (
                "👋 Welcome to the Crelec Blower Selection Assistant!\n\n"
                "I'll help you find the optimal blower configuration and show you "
                "potential energy savings through smart sizing.\n\n"
                "First, what type of operation do you need?\n\n"
                "1️⃣ **Compression** (Blowing air into tanks, aeration, pressurizing)\n"
                "2️⃣ **Vacuum** (Suction, extraction, pneumatic conveying)\n\n"
                "Please type 1 for Compression or 2 for Vacuum:"
            ),
            'quick_buttons': ['Compression', 'Vacuum'],
            'state': 'operation_type'
        }

    def _handle_operation_type(self, session: UserSession, user_input: str) -> Dict:
        """Handle operation type selection"""
        user_input_lower = user_input.lower().strip()

        # Parse operation type
        if '1' in user_input or 'compression' in user_input_lower or 'blowing' in user_input_lower or 'aeration' in user_input_lower:
            operation = 'compression'
            operation_display = 'Compression/Blowing'
            examples = "(aeration tanks, oxidation, pressurizing)"
        elif '2' in user_input or 'vacuum' in user_input_lower or 'suction' in user_input_lower:
            operation = 'vacuum'
            operation_display = 'Vacuum/Suction'
            examples = "(material handling, extraction, dewatering)"
        else:
            return {
                'message': (
                    "Please select the operation type:\n"
                    "1 - Compression (for blowing air into systems)\n"
                    "2 - Vacuum (for suction applications)"
                ),
                'state': 'operation_type'
            }

        # Store operation type
        session.data['operation_type'] = operation
        session.state = ChatState.APPLICATION

        return {
            'message': (
                f"✅ **{operation_display}** selected {examples}\n\n"
                "Now, what's your specific application?\n\n"
                "1️⃣ **Waste Water Treatment** (sewage, industrial effluent)\n"
                "2️⃣ **Fish Farming / Aquaculture** (hatcheries, grow-out)\n"
                "3️⃣ **Industrial Process** (mixing, oxidation, pneumatic)\n"
                "4️⃣ **Not Sure** (I'll help you determine)\n\n"
                "Please type 1, 2, 3, or describe your application:"
            ),
            'quick_buttons': ['Waste Water', 'Fish Farm', 'Industrial', 'Help Me'],
            'state': 'application'
        }

    def _handle_application(self, session: UserSession, user_input: str) -> Dict:
        """Handle application selection"""
        user_input_lower = user_input.lower().strip()

        # Check for help request
        if '4' in user_input or 'help' in user_input_lower or 'not sure' in user_input_lower:
            return {
                'message': (
                    "Let me help you identify your application:\n\n"
                    "**Waste Water Treatment** if you have:\n"
                    "• Aeration tanks with diffusers\n"
                    "• Activated sludge process\n"
                    "• SBR or MBR systems\n\n"
                    "**Fish Farming** if you have:\n"
                    "• Fish tanks or ponds\n"
                    "• Hatchery systems\n"
                    "• Live fish holding\n\n"
                    "**Industrial** if you have:\n"
                    "• Chemical oxidation\n"
                    "• Pneumatic conveying\n"
                    "• Agitation/mixing\n\n"
                    "Which sounds like your application?"
                ),
                'state': 'application'
            }

        # Try to match application
        app_type = None
        for key, value in self.quick_applications.items():
            if key in user_input_lower:
                app_type = value
                break

        if not app_type:
            return {
                'message': (
                    "I didn't understand that. Please choose:\n"
                    "1 - Waste Water Treatment\n"
                    "2 - Fish Farming\n"
                    "3 - Industrial Process"
                ),
                'state': 'application'
            }

        # Store and move forward
        session.data['application_type'] = app_type
        session.has_application = True
        session.state = ChatState.LOCATION

        app_display = app_type.replace('_', ' ').title()

        return {
            'message': (
                f"✅ **{app_display}** - Great choice!\n\n"
                f"{'This is critical for biological treatment efficiency.' if app_type == 'waste_water' else ''}"
                f"{'Fish welfare depends on proper oxygenation!' if app_type == 'fish_hatchery' else ''}"
                f"{'Industrial processes need reliable air supply.' if app_type == 'industrial' else ''}\n\n"
                "📍 **Where will the blowers be installed?**\n"
                "This helps me calculate altitude corrections for accurate sizing.\n\n"
                "You can tell me:\n"
                "• City name (e.g., 'Johannesburg')\n"
                "• Altitude (e.g., '1500m')\n"
                "• General area (e.g., 'coastal', 'inland')\n\n"
                "Location or altitude:"
            ),
            'quick_buttons': ['Johannesburg', 'Cape Town', 'Durban', 'Coastal'],
            'state': 'location'
        }

    def _handle_location(self, session: UserSession, user_input: str) -> Dict:
        """Handle location input with smart recognition"""
        from location_handler import LocationHandler

        handler = LocationHandler()
        location_data = handler.process_location_input(user_input)

        # Store location data
        session.data['location_text'] = user_input
        session.data['altitude'] = location_data.altitude
        session.data['temperature'] = location_data.temperature
        session.has_location = True
        session.state = ChatState.TANK_SIZE

        # Calculate correction impact
        corrections = handler.calculate_correction_factors(
            location_data.altitude,
            location_data.temperature
        )

        impact_msg = ""
        if corrections['pressure_correction'] < 0.85:
            impact_msg = f"\n⚠️ At this altitude, blowers need to be ~{((1/corrections['pressure_correction'])-1)*100:.0f}% larger!"

        return {
            'message': (
                f"{location_data.message}\n"
                f"{impact_msg}\n\n"
                "📐 **Now, let's size your aeration system.**\n\n"
                "How would you like to specify your tank size?\n\n"
                "1️⃣ **Enter dimensions** (I'll calculate volume)\n"
                "2️⃣ **Enter total volume** (if you know it)\n"
                "3️⃣ **Multiple tanks** (for tank farms)\n"
                "4️⃣ **Show typical sizes** (for reference)\n\n"
                "Choose an option or enter dimensions (L × W × Depth in meters):"
            ),
            'quick_buttons': ['Enter Dimensions', 'Enter Volume', 'Multiple Tanks', 'Typical Sizes'],
            'state': 'tank_size'
        }

    def _handle_tank_size(self, session: UserSession, user_input: str) -> Dict:
        """Handle tank size input"""
        user_input_lower = user_input.lower().strip()

        # Show typical sizes
        if '4' in user_input or 'typical' in user_input_lower:
            return {
                'message': (
                    "📊 **Typical Tank Sizes:**\n\n"
                    "**Small** (16 m³): 4m × 2m × 2m deep\n"
                    "• Single family homes\n"
                    "• Small businesses\n\n"
                    "**Medium** (45 m³): 6m × 3m × 2.5m deep\n"
                    "• Small communities\n"
                    "• Fish hatcheries\n\n"
                    "**Large** (150 m³): 10m × 5m × 3m deep\n"
                    "• Municipal plants\n"
                    "• Industrial facilities\n\n"
                    "**Extra Large** (480 m³): 15m × 8m × 4m deep\n"
                    "• Large municipalities\n"
                    "• Major industries\n\n"
                    "Enter your tank dimensions (L W D) or type 'small', 'medium', 'large':"
                ),
                'state': 'tank_size'
            }

        # Check for typical size keywords
        for size_key, dimensions in self.typical_tanks.items():
            if size_key in user_input_lower:
                session.data['tank_length'] = dimensions['length']
                session.data['tank_width'] = dimensions['width']
                session.data['tank_depth'] = dimensions['depth']
                session.data['tank_volume'] = dimensions['volume']
                session.data['num_tanks'] = 1
                session.state = ChatState.TANK_DETAILS

                return {
                    'message': (
                        f"✅ Using {size_key} tank size: "
                        f"{dimensions['length']}m × {dimensions['width']}m × {dimensions['depth']}m "
                        f"= {dimensions['volume']} m³\n\n"
                        "Do you have multiple tanks? (Enter number or 'no' for single tank):"
                    ),
                    'state': 'tank_details'
                }

        # Parse dimensions
        try:
            # Try to extract numbers
            import re
            numbers = re.findall(r'\d+\.?\d*', user_input)

            if len(numbers) == 3:
                length = float(numbers[0])
                width = float(numbers[1])
                depth = float(numbers[2])

                session.data['tank_length'] = length
                session.data['tank_width'] = width
                session.data['tank_depth'] = depth
                session.data['tank_volume'] = length * width * depth
                session.data['num_tanks'] = 1
                session.state = ChatState.TANK_DETAILS

                return {
                    'message': (
                        f"✅ Tank dimensions captured:\n"
                        f"• Size: {length}m × {width}m × {depth}m deep\n"
                        f"• Volume: {length * width * depth:.0f} m³\n\n"
                        "How many tanks do you have? (Enter number or '1' for single tank):"
                    ),
                    'state': 'tank_details'
                }
            elif len(numbers) == 1:
                # Direct volume entry
                volume = float(numbers[0])
                # Estimate dimensions (cube root)
                side = (volume ** (1/3))
                session.data['tank_length'] = side * 1.5
                session.data['tank_width'] = side
                session.data['tank_depth'] = side * 0.67
                session.data['tank_volume'] = volume
                session.data['num_tanks'] = 1
                session.state = ChatState.TANK_DETAILS

                return {
                    'message': (
                        f"✅ Tank volume: {volume} m³\n\n"
                        "How many tanks do you have? (Enter number or '1' for single tank):"
                    ),
                    'state': 'tank_details'
                }

        except (ValueError, IndexError):
            pass

        return {
            'message': (
                "Please enter tank dimensions as three numbers (length width depth in meters)\n"
                "For example: '6 3 2' or '6m × 3m × 2m'"
            ),
            'state': 'tank_size'
        }

    def _handle_tank_details(self, session: UserSession, user_input: str) -> Dict:
        """Handle number of tanks"""
        user_input_lower = user_input.lower().strip()

        # Parse number of tanks
        import re
        numbers = re.findall(r'\d+', user_input)

        if numbers:
            num_tanks = int(numbers[0])
        elif 'no' in user_input_lower or 'single' in user_input_lower or 'one' in user_input_lower:
            num_tanks = 1
        else:
            return {
                'message': "How many tanks? Please enter a number:",
                'state': 'tank_details'
            }

        session.data['num_tanks'] = num_tanks
        total_volume = session.data['tank_volume'] * num_tanks
        session.has_tank_size = True
        session.state = ChatState.LOAD_PATTERN

        return {
            'message': (
                f"✅ System size confirmed:\n"
                f"• {num_tanks} tank(s) × {session.data['tank_volume']:.0f} m³ = {total_volume:.0f} m³ total\n\n"
                "⚡ **Load Pattern Analysis**\n"
                "This is crucial for energy optimization!\n\n"
                "Does your air demand vary throughout the day?\n\n"
                "1️⃣ **Constant** - Same demand 24/7\n"
                "2️⃣ **Variable** - Changes with time (typical for waste water)\n"
                "3️⃣ **Don't know** - I'll use typical patterns\n\n"
                "Select 1, 2, or 3:"
            ),
            'quick_buttons': ['Constant', 'Variable', 'Use Typical'],
            'state': 'load_pattern'
        }

    def _handle_load_pattern(self, session: UserSession, user_input: str) -> Dict:
        """Handle load pattern selection"""
        user_input_lower = user_input.lower().strip()

        if '1' in user_input or 'constant' in user_input_lower:
            load_pattern = 'constant'
            session.data['load_varies'] = False
        elif '2' in user_input or 'variable' in user_input_lower:
            load_pattern = 'variable'
            session.data['load_varies'] = True
        else:
            load_pattern = 'typical'
            session.data['load_varies'] = True

        session.has_load_pattern = True
        session.state = ChatState.CALCULATING

        # Trigger calculation
        return self._handle_calculating(session, '')

    def _handle_calculating(self, session: UserSession, user_input: str) -> Dict:
        """Perform calculations and show results"""

        # Create calculation inputs
        inputs = CalculationInputs(
            tank_length=session.data.get('tank_length', 6),
            tank_width=session.data.get('tank_width', 3),
            tank_depth=session.data.get('tank_depth', 2),
            num_tanks=session.data.get('num_tanks', 1),
            location_text=session.data.get('location_text', ''),
            altitude=session.data.get('altitude'),
            temperature=session.data.get('temperature'),
            application_type=session.data.get('application_type', 'waste_water'),
            pipe_length=100,  # Default
            pipe_diameter=150,  # Default
            num_bends=4  # Default
        )

        # Calculate
        results = self.calculator.calculate(inputs)
        session.calculation_results = results
        session.state = ChatState.RESULTS

        # Format comparison table for display
        comparison_html = self._format_comparison_table_html(results.comparison_table)

        # Find best option
        best_config = results.comparison_table[1] if len(results.comparison_table) > 1 else results.comparison_table[0]

        return {
            'message': (
                "🎯 **CALCULATION COMPLETE!**\n\n"
                f"**Your Requirements:**\n"
                f"• Airflow needed: {results.required_airflow:.0f} m³/hr\n"
                f"• Pressure needed: {results.required_pressure:.0f} mbar\n"
                f"• Location factor: {(1/results.altitude_correction - 1)*100:.0f}% oversizing for altitude\n\n"
                "**💰 ENERGY SAVINGS COMPARISON:**\n"
            ),
            'comparison_table': comparison_html,
            'summary': (
                f"\n**✅ RECOMMENDED: {best_config['configuration']}**\n"
                f"• Configuration: {best_config['num_blowers']} blowers @ {best_config['size_each']} each\n"
                f"• Energy Savings: {best_config['energy_savings']}\n"
                f"• Annual Savings: R{results.annual_savings_currency:,.0f}\n"
                f"• Payback Period: {results.payback_months:.0f} months\n\n"
                f"{best_config['notes']}\n\n"
                "Would you like:\n"
                "1. See matching blower products\n"
                "2. Get detailed PDF quote\n"
                "3. Adjust parameters"
            ),
            'quick_buttons': ['Show Products', 'Get Quote', 'Adjust'],
            'state': 'results',
            'calculation_complete': True
        }

    def _handle_results(self, session: UserSession, user_input: str) -> Dict:
        """Handle results state options"""
        # To be implemented - product matching, quote generation, etc.
        return {
            'message': "Product matching will be implemented next...",
            'state': 'results'
        }

    def _handle_quote(self, session: UserSession, user_input: str) -> Dict:
        """Handle quote generation"""
        # To be implemented
        return {
            'message': "Quote generation will be implemented next...",
            'state': 'quote'
        }

    def _format_comparison_table_html(self, table_data: List[Dict]) -> str:
        """Format comparison table as HTML for display"""
        html = """
        <table class='comparison-table'>
        <thead>
            <tr>
                <th>Configuration</th>
                <th>Blowers</th>
                <th>Size Each</th>
                <th>Energy Savings</th>
                <th>Redundancy</th>
                <th>Flexibility</th>
            </tr>
        </thead>
        <tbody>
        """

        for row in table_data:
            row_class = 'recommended' if row.get('recommended') else ''
            prefix = '⭐ ' if row.get('recommended') else ''

            # Highlight energy savings
            energy_class = 'savings-high' if '30%' in str(row['energy_savings']) else ''

            html += f"""
            <tr class='{row_class}'>
                <td>{prefix}{row['configuration']}</td>
                <td>{row['num_blowers']}</td>
                <td>{row['size_each']}</td>
                <td class='{energy_class}'><strong>{row['energy_savings']}</strong></td>
                <td>{row['redundancy']}</td>
                <td>{row['turndown_range']}</td>
            </tr>
            """

        html += """
        </tbody>
        </table>
        """

        return html


# Example usage
if __name__ == "__main__":
    chat = ImprovedChatFlow()

    # Simulate conversation
    session_id = "test123"

    # Welcome
    response = chat.process_message(session_id, "start")
    print("Bot:", response['message'][:200] + "...")

    # Application
    response = chat.process_message(session_id, "waste water")
    print("\nBot:", response['message'][:200] + "...")

    # Location
    response = chat.process_message(session_id, "Johannesburg")
    print("\nBot:", response['message'][:200] + "...")

    # Tank size
    response = chat.process_message(session_id, "6 3 2")
    print("\nBot:", response['message'][:200] + "...")

    # Number of tanks
    response = chat.process_message(session_id, "3")
    print("\nBot:", response['message'][:200] + "...")

    # Load pattern
    response = chat.process_message(session_id, "variable")
    print("\nBot:", response.get('summary', response['message'])[:500] + "...")