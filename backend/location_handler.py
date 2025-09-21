"""
Smart Location Handler for Blower Calculator
=============================================
Intelligently extracts altitude and temperature from various user inputs
with fallback strategies and clear communication of assumptions.

Author: Liberlocus for Crelec S.A.
Date: September 2025
"""

import re
from difflib import get_close_matches
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import json


@dataclass
class LocationData:
    """Data class for location information"""
    altitude: float  # meters above sea level
    temperature: float  # degrees Celsius
    city: Optional[str] = None
    confidence: str = 'low'  # 'high', 'medium', 'low'
    altitude_source: str = 'user'  # 'user', 'lookup', 'default'
    temp_source: str = 'user'  # 'user', 'estimated', 'default'
    message: str = ''


class LocationHandler:
    """
    Handles intelligent extraction and lookup of location data
    for altitude and temperature corrections in blower calculations.
    """

    def __init__(self):
        self.sa_locations = self._load_sa_database()

    def _load_sa_database(self) -> Dict:
        """
        Load South African cities database with altitude and temperature data
        """
        return {
            # Major Cities
            'johannesburg': {
                'altitude': 1750,
                'temp_summer': 26,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': ['joburg', 'jhb', 'jozi', 'egoli']
            },
            'pretoria': {
                'altitude': 1350,
                'temp_summer': 28,
                'temp_winter': 18,
                'temp_avg': 22,
                'aliases': ['tshwane', 'pta']
            },
            'cape town': {
                'altitude': 50,
                'temp_summer': 26,
                'temp_winter': 13,
                'temp_avg': 18,
                'aliases': ['kaapstad', 'mother city', 'cpt']
            },
            'durban': {
                'altitude': 10,
                'temp_summer': 28,
                'temp_winter': 20,
                'temp_avg': 24,
                'aliases': ['ethekwini', 'dbn']
            },
            'port elizabeth': {
                'altitude': 60,
                'temp_summer': 25,
                'temp_winter': 17,
                'temp_avg': 20,
                'aliases': ['gqeberha', 'pe', 'nelson mandela bay']
            },
            'bloemfontein': {
                'altitude': 1400,
                'temp_summer': 30,
                'temp_winter': 15,
                'temp_avg': 20,
                'aliases': ['bloem', 'mangaung']
            },
            'east london': {
                'altitude': 50,
                'temp_summer': 26,
                'temp_winter': 18,
                'temp_avg': 21,
                'aliases': ['buffalo city', 'el']
            },
            'kimberley': {
                'altitude': 1200,
                'temp_summer': 32,
                'temp_winter': 17,
                'temp_avg': 22,
                'aliases': ['diamond city']
            },
            'nelspruit': {
                'altitude': 660,
                'temp_summer': 30,
                'temp_winter': 20,
                'temp_avg': 24,
                'aliases': ['mbombela']
            },
            'polokwane': {
                'altitude': 1230,
                'temp_summer': 28,
                'temp_winter': 18,
                'temp_avg': 21,
                'aliases': ['pietersburg']
            },
            'rustenburg': {
                'altitude': 1170,
                'temp_summer': 30,
                'temp_winter': 18,
                'temp_avg': 23,
                'aliases': ['phokeng']
            },
            'george': {
                'altitude': 200,
                'temp_summer': 24,
                'temp_winter': 15,
                'temp_avg': 18,
                'aliases': []
            },

            # Industrial Areas
            'vanderbijlpark': {
                'altitude': 1480,
                'temp_summer': 28,
                'temp_winter': 16,
                'temp_avg': 21,
                'aliases': ['vaal triangle']
            },
            'midrand': {
                'altitude': 1550,
                'temp_summer': 26,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': []
            },
            'centurion': {
                'altitude': 1450,
                'temp_summer': 28,
                'temp_winter': 17,
                'temp_avg': 21,
                'aliases': []
            },
            'germiston': {
                'altitude': 1665,
                'temp_summer': 26,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': []
            },
            'benoni': {
                'altitude': 1650,
                'temp_summer': 26,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': []
            },
            'boksburg': {
                'altitude': 1630,
                'temp_summer': 26,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': []
            },

            # Coastal (Generic)
            'coastal': {
                'altitude': 50,
                'temp_summer': 26,
                'temp_winter': 18,
                'temp_avg': 22,
                'aliases': ['coast', 'seaside', 'beach', 'sea level']
            },

            # Inland (Generic)
            'inland': {
                'altitude': 1200,
                'temp_summer': 28,
                'temp_winter': 16,
                'temp_avg': 20,
                'aliases': ['interior', 'highveld']
            }
        }

    def extract_from_text(self, text: str) -> Dict:
        """
        Extract location information from user text using patterns
        """
        result = {
            'altitude': None,
            'temperature': None,
            'city': None,
            'raw_text': text
        }

        # Clean text
        text_lower = text.lower().strip()

        # Pattern 1: Direct altitude (e.g., "1500m", "1500 meters", "altitude 1500")
        altitude_patterns = [
            r'(\d+)\s*m(?:eters?)?(?:\s+above\s+sea\s+level)?',
            r'altitude\s+(?:is\s+)?(\d+)',
            r'(\d+)\s*(?:meters?|m)\s+altitude',
            r'elevation\s+(?:is\s+)?(\d+)',
        ]

        for pattern in altitude_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['altitude'] = float(match.group(1))
                break

        # Pattern 2: Temperature (e.g., "25°C", "25 degrees", "temp 25")
        temp_patterns = [
            r'(\d+)\s*°?\s*c(?:elsius)?',
            r'temperature\s+(?:is\s+)?(\d+)',
            r'temp\s+(?:is\s+)?(\d+)',
            r'(\d+)\s*degrees?',
            r'average\s+(?:temp(?:erature)?\s+)?(\d+)',
        ]

        for pattern in temp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                temp_value = float(match.group(1))
                # Sanity check for temperature
                if -10 <= temp_value <= 50:
                    result['temperature'] = temp_value
                break

        # Pattern 3: City/Location names
        # Check all cities and their aliases
        for city, data in self.sa_locations.items():
            # Check main city name
            if city in text_lower:
                result['city'] = city
                break
            # Check aliases
            for alias in data.get('aliases', []):
                if alias in text_lower:
                    result['city'] = city
                    break
            if result['city']:
                break

        # Special keywords
        if 'sea level' in text_lower or 'coastal' in text_lower:
            result['city'] = 'coastal'
        elif 'inland' in text_lower or 'highveld' in text_lower:
            result['city'] = 'inland'

        return result

    def lookup_city_data(self, city: str) -> Optional[LocationData]:
        """
        Lookup altitude and temperature data for a city
        """
        city_lower = city.lower().strip()

        # Direct match
        if city_lower in self.sa_locations:
            data = self.sa_locations[city_lower]
            return LocationData(
                altitude=data['altitude'],
                temperature=data['temp_avg'],
                city=city,
                confidence='high',
                altitude_source='lookup',
                temp_source='lookup',
                message=f"Using data for {city.title()}"
            )

        # Check aliases
        for city_name, data in self.sa_locations.items():
            if city_lower in data.get('aliases', []):
                return LocationData(
                    altitude=data['altitude'],
                    temperature=data['temp_avg'],
                    city=city_name,
                    confidence='high',
                    altitude_source='lookup',
                    temp_source='lookup',
                    message=f"Found {city} as {city_name.title()}"
                )

        # Fuzzy match
        city_names = list(self.sa_locations.keys())
        matches = get_close_matches(city_lower, city_names, n=1, cutoff=0.6)

        if matches:
            matched_city = matches[0]
            data = self.sa_locations[matched_city]
            return LocationData(
                altitude=data['altitude'],
                temperature=data['temp_avg'],
                city=matched_city,
                confidence='medium',
                altitude_source='lookup',
                temp_source='lookup',
                message=f"Assuming you meant {matched_city.title()}"
            )

        return None

    def process_location_input(self, user_input: str) -> LocationData:
        """
        Main method to process user location input with smart fallbacks
        """
        # Extract what we can from the text
        extracted = self.extract_from_text(user_input)

        # Initialize location data
        location = LocationData(
            altitude=extracted.get('altitude'),
            temperature=extracted.get('temperature'),
            city=extracted.get('city')
        )

        # If we have a city but missing altitude/temp, lookup
        if location.city and (location.altitude is None or location.temperature is None):
            city_data = self.lookup_city_data(location.city)
            if city_data:
                if location.altitude is None:
                    location.altitude = city_data.altitude
                    location.altitude_source = 'lookup'
                if location.temperature is None:
                    location.temperature = city_data.temperature
                    location.temp_source = 'lookup'
                location.confidence = city_data.confidence
                location.message = city_data.message

        # Apply defaults if still missing
        if location.altitude is None:
            location.altitude = 500  # SA average
            location.altitude_source = 'default'
            location.confidence = 'low'
        else:
            location.altitude_source = location.altitude_source or 'user'

        if location.temperature is None:
            location.temperature = 20  # Moderate default
            location.temp_source = 'default'
            location.confidence = 'low' if location.confidence != 'low' else 'low'
        else:
            location.temp_source = location.temp_source or 'user'

        # Generate appropriate message
        location.message = self._generate_message(location)

        return location

    def _generate_message(self, location: LocationData) -> str:
        """
        Generate a clear message about what data we're using
        """
        messages = []

        # Altitude message
        if location.altitude_source == 'user':
            messages.append(f"✓ Using altitude: {location.altitude:.0f}m (as specified)")
        elif location.altitude_source == 'lookup':
            messages.append(f"✓ Found altitude: {location.altitude:.0f}m")
        else:
            messages.append(f"ℹ Using default altitude: {location.altitude:.0f}m (please specify for better accuracy)")

        # Temperature message
        if location.temp_source == 'user':
            messages.append(f"✓ Using temperature: {location.temperature:.0f}°C (as specified)")
        elif location.temp_source == 'lookup':
            messages.append(f"✓ Using average temperature: {location.temperature:.0f}°C")
        else:
            messages.append(f"ℹ Using default temperature: {location.temperature:.0f}°C (please specify for better accuracy)")

        # Add city if identified
        if location.city and location.city not in ['coastal', 'inland']:
            messages.insert(0, f"📍 Location: {location.city.title()}")

        # Confidence indicator
        if location.confidence == 'low':
            messages.append("💡 Tip: Provide city name or altitude for more accurate results")

        return "\n".join(messages)

    def calculate_correction_factors(self, altitude: float, temperature: float) -> Dict[str, float]:
        """
        Calculate altitude and temperature correction factors for blower performance
        """
        # Standard conditions
        P0 = 101325  # Pa at sea level
        T0 = 288.15  # K (15°C standard)

        # Pressure at altitude (barometric formula)
        P = P0 * (1 - 0.0065 * altitude / T0) ** 5.256

        # Temperature in Kelvin
        T = temperature + 273.15

        # Density ratios
        pressure_ratio = P / P0
        temp_ratio = T0 / T
        density_ratio = pressure_ratio * temp_ratio

        # Correction factors
        factors = {
            'pressure_ratio': pressure_ratio,
            'temperature_ratio': temp_ratio,
            'density_ratio': density_ratio,
            'pressure_correction': density_ratio,  # Blower pressure capability
            'flow_correction': 1.0,  # Volume flow stays same
            'mass_flow_correction': density_ratio,  # Mass flow reduces
            'power_correction': density_ratio,  # Power requirement reduces
            'oversize_factor': 1 / density_ratio if density_ratio < 1 else 1.0
        }

        return factors

    def format_correction_message(self, factors: Dict[str, float], altitude: float, temperature: float) -> str:
        """
        Format a user-friendly message about corrections being applied
        """
        messages = []

        # Header
        messages.append(f"🔧 Altitude/Temperature Corrections:")
        messages.append(f"   Altitude: {altitude:.0f}m | Temperature: {temperature:.0f}°C")

        # Impact on performance
        pressure_impact = (1 - factors['pressure_correction']) * 100
        if abs(pressure_impact) > 5:
            if pressure_impact > 0:
                messages.append(f"   ⬇ Pressure capacity reduced by {pressure_impact:.0f}%")
            else:
                messages.append(f"   ⬆ Pressure capacity increased by {-pressure_impact:.0f}%")

        # Oversizing recommendation
        if factors['oversize_factor'] > 1.1:
            messages.append(f"   ⚠️ Blower should be oversized by {(factors['oversize_factor']-1)*100:.0f}%")
        elif factors['oversize_factor'] > 1.05:
            messages.append(f"   ℹ Blower should be oversized by {(factors['oversize_factor']-1)*100:.0f}%")

        return "\n".join(messages)


# Example usage and testing
if __name__ == "__main__":
    handler = LocationHandler()

    # Test cases
    test_inputs = [
        "I'm in Johannesburg",
        "altitude 1500m, temperature 25°C",
        "We're at sea level, about 30 degrees usually",
        "Pretoria area",
        "1420 meters above sea level",
        "coastal installation",
        "jhb, average temp",
        "somewhere inland",
        ""  # Empty input
    ]

    print("LOCATION HANDLER TEST RESULTS")
    print("=" * 50)

    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        print("-" * 30)

        location = handler.process_location_input(test_input)
        print(location.message)

        factors = handler.calculate_correction_factors(location.altitude, location.temperature)
        print(handler.format_correction_message(factors, location.altitude, location.temperature))
        print()