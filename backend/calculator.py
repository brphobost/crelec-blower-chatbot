"""
Simple Blower Calculator Module
Starting with basic calculations, designed to be extended later
"""

from typing import Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class CalculationInput:
    """Input parameters for blower calculation"""
    length: float  # meters
    width: float   # meters
    height: float  # meters
    altitude: float  # meters above sea level
    application_type: str = "waste_water"
    safety_factor: float = 1.2
    air_changes_per_hour: Optional[float] = None


@dataclass
class CalculationResult:
    """Result of blower calculation"""
    airflow_required: float  # m³/hr
    pressure_required: float  # mbar
    power_estimate: float  # kW
    tank_volume: float  # m³
    notes: list


class BlowerCalculator:
    """
    Simple calculator for blower selection
    Will be enhanced with complex calculations later
    """

    # Default air changes per hour for different applications
    AIR_CHANGES_DEFAULT = {
        "waste_water": 6,
        "fish_hatchery": 10,
        "general": 4
    }

    def calculate_basic(self, input_data: CalculationInput) -> CalculationResult:
        """
        Basic calculation for MVP
        Future: Add pipe losses, multiple blowers, different geometries
        """
        # Calculate tank volume
        tank_volume = input_data.length * input_data.width * input_data.height

        # Determine air changes per hour
        if input_data.air_changes_per_hour:
            air_changes = input_data.air_changes_per_hour
        else:
            air_changes = self.AIR_CHANGES_DEFAULT.get(
                input_data.application_type,
                self.AIR_CHANGES_DEFAULT["general"]
            )

        # Calculate basic airflow requirement
        airflow_base = tank_volume * air_changes
        airflow_required = airflow_base * input_data.safety_factor

        # Calculate pressure requirement with altitude adjustment
        pressure_required = self._calculate_pressure(
            input_data.height,
            input_data.altitude
        )

        # Estimate power requirement (simplified)
        power_estimate = self._estimate_power(airflow_required, pressure_required)

        # Generate notes for transparency
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
        """
        Calculate pressure requirement based on water depth and altitude
        Simplified version - will add complexity later
        """
        # Hydrostatic pressure (1m water = 98.1 mbar)
        water_pressure = depth * 98.1

        # Add system losses (simplified - typically 100-200 mbar)
        system_losses = 150

        # Altitude correction (approximately 12 mbar per 100m)
        altitude_correction = (altitude / 100) * 12

        total_pressure = water_pressure + system_losses + altitude_correction

        return total_pressure

    def _estimate_power(self, airflow: float, pressure: float) -> float:
        """
        Estimate power requirement
        Simplified formula - actual depends on efficiency
        """
        # Convert units for calculation
        airflow_m3_s = airflow / 3600  # Convert m³/hr to m³/s
        pressure_pa = pressure * 100  # Convert mbar to Pascal

        # Theoretical power (W) = Flow * Pressure
        theoretical_power = airflow_m3_s * pressure_pa

        # Account for blower efficiency (typical 50-70%)
        efficiency = 0.6
        actual_power = theoretical_power / efficiency

        # Convert to kW
        power_kw = actual_power / 1000

        return power_kw

    def calculate_from_form_data(self, form_data: Dict) -> Dict:
        """
        Helper method to calculate from raw form data
        Returns JSON-serializable dict
        """
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


# Future enhancements placeholder
class AdvancedCalculator(BlowerCalculator):
    """
    Placeholder for advanced calculations
    To be implemented based on full spreadsheet logic
    """

    def calculate_pipe_losses(self):
        """TODO: Add pipe friction calculations"""
        pass

    def calculate_multiple_blowers(self):
        """TODO: Handle series/parallel configurations"""
        pass

    def calculate_cylinder_tank(self):
        """TODO: Support different geometries"""
        pass