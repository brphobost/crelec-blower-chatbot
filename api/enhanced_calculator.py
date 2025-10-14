"""
Enhanced Blower Selection Calculator
=====================================
Implements professional-grade calculations including:
- Pipe friction and fitting losses
- Diffuser pressure drops
- Multiple tank configurations
- Detailed breakdown of all components

Based on CALCULATIONS.md documentation
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PipeSystem:
    """Pipe system specifications"""
    diameter: float  # mm
    length: float    # meters
    num_bends: int   # number of 90° bends
    material: str = 'smooth'  # smooth, rough, galvanized


@dataclass
class CalculationBreakdown:
    """Detailed breakdown of all calculation components"""
    # Airflow components
    base_airflow_m3_min: float
    base_airflow_m3_hr: float
    corrected_airflow_m3_hr: float

    # Pressure components (all in mbar)
    static_pressure: float
    pipe_friction_loss: float
    fitting_losses: float
    diffuser_loss: float
    subtotal_pressure: float
    safety_margin: float
    total_pressure: float
    altitude_corrected_pressure: float

    # Factors applied
    altitude_correction: float
    safety_factor: float
    specific_gravity: float

    # Additional info
    pipe_velocity: float  # m/s
    messages: List[str]
    warnings: List[str]


class EnhancedBlowerCalculator:
    """
    Professional blower selection calculator with detailed engineering calculations
    """

    def __init__(self):
        # Diffuser pressure drops (mbar)
        self.diffuser_pressures = {
            'fine': 250,      # Fine bubble membrane
            'disc': 200,      # Ceramic disc
            'coarse': 50,     # Coarse bubble/perforated pipe
            'tube': 80,       # Tube diffusers
            'jet': 30,        # Jet aerators
            'custom': 100     # Default for custom systems
        }

        # K-factors for fittings
        self.k_factors = {
            '90_bend': 0.9,
            '45_bend': 0.4,
            'tee': 1.8,
            'valve_open': 0.2,
            'entrance': 0.5,
            'exit': 1.0
        }

        # Pipe friction factors (smooth pipes)
        self.friction_factors = {
            'smooth': 0.025,
            'galvanized': 0.030,
            'rough': 0.035,
            'very_rough': 0.040
        }

        # Application-specific parameters
        self.app_params = {
            'waste_water': {
                'airflow_factor': 0.25,  # m³/min per m²
                'safety_factor': 1.2,
                'specific_gravity': 1.05,
                'default_diffuser': 'fine'
            },
            'fish_hatchery': {
                'airflow_factor': 0.002,  # m³/min per m²
                'safety_factor': 1.5,
                'specific_gravity': 1.0,
                'default_diffuser': 'coarse'
            },
            'industrial': {
                'air_changes_per_hour': 2,
                'safety_factor': 1.3,
                'specific_gravity': 1.0,
                'default_diffuser': 'disc'
            }
        }

    def calculate(self,
                  # Tank parameters
                  tank_length: float,
                  tank_width: float,
                  tank_depth: float,
                  num_tanks: int = 1,
                  tank_config: str = 'parallel',

                  # Application
                  application: str = 'waste_water',

                  # Location
                  altitude: float = 0,
                  temperature: float = 20,

                  # Pipe system
                  pipe_diameter: Optional[float] = None,
                  pipe_length: Optional[float] = None,
                  num_bends: Optional[int] = None,

                  # Diffuser
                  diffuser_type: Optional[str] = None,
                  diffuser_depth: Optional[float] = None,

                  # Optional overrides
                  safety_factor: Optional[float] = None) -> Dict:
        """
        Calculate blower requirements with detailed breakdown

        Returns:
            Dictionary containing requirements and detailed breakdown
        """

        # Initialize breakdown
        breakdown = CalculationBreakdown(
            base_airflow_m3_min=0,
            base_airflow_m3_hr=0,
            corrected_airflow_m3_hr=0,
            static_pressure=0,
            pipe_friction_loss=0,
            fitting_losses=0,
            diffuser_loss=0,
            subtotal_pressure=0,
            safety_margin=0,
            total_pressure=0,
            altitude_corrected_pressure=0,
            altitude_correction=1.0,
            safety_factor=1.0,
            specific_gravity=1.0,
            pipe_velocity=0,
            messages=[],
            warnings=[]
        )

        # Get application parameters
        app_data = self.app_params.get(application, self.app_params['industrial'])

        # Use provided safety factor or default
        if safety_factor:
            breakdown.safety_factor = safety_factor
        else:
            breakdown.safety_factor = app_data.get('safety_factor', 1.2)

        breakdown.specific_gravity = app_data.get('specific_gravity', 1.0)

        # Calculate tank parameters
        tank_area = tank_length * tank_width
        tank_volume = tank_area * tank_depth

        # Use actual diffuser depth or tank depth
        actual_diffuser_depth = diffuser_depth if diffuser_depth else tank_depth

        # 1. CALCULATE BASE AIRFLOW
        if application in ['waste_water', 'fish_hatchery']:
            # Area-based calculation
            airflow_factor = app_data.get('airflow_factor', 0.25)
            breakdown.base_airflow_m3_min = tank_area * airflow_factor

            # Handle multiple tanks
            if num_tanks > 1:
                if tank_config == 'parallel':
                    # Parallel: multiply total flow
                    breakdown.base_airflow_m3_min *= num_tanks
                    breakdown.messages.append(f"Parallel tanks: {num_tanks} × {tank_area:.1f}m² × {airflow_factor}")
                else:
                    # Series: same flow through all
                    breakdown.messages.append(f"Series tanks: Flow through {num_tanks} tanks sequentially")
        else:
            # Industrial: volume-based with air changes
            air_changes = app_data.get('air_changes_per_hour', 2)
            breakdown.base_airflow_m3_min = (tank_volume * air_changes * num_tanks) / 60
            breakdown.messages.append(f"Industrial: {tank_volume:.1f}m³ × {air_changes} changes/hr")

        breakdown.base_airflow_m3_hr = breakdown.base_airflow_m3_min * 60

        # 2. CALCULATE STATIC PRESSURE
        breakdown.static_pressure = actual_diffuser_depth * 98.1 * breakdown.specific_gravity

        # 3. CALCULATE PIPE LOSSES (if pipe data provided)
        if pipe_diameter and pipe_length:
            pipe_diameter_m = pipe_diameter / 1000  # Convert mm to m
            pipe_area = math.pi * (pipe_diameter_m / 2) ** 2

            # Calculate air velocity in pipe
            airflow_m3_s = breakdown.base_airflow_m3_min / 60
            breakdown.pipe_velocity = airflow_m3_s / pipe_area

            # Check velocity limits
            if breakdown.pipe_velocity > 30:
                breakdown.warnings.append(f"High pipe velocity: {breakdown.pipe_velocity:.1f} m/s (>30 m/s)")
            elif breakdown.pipe_velocity < 5:
                breakdown.messages.append(f"Low pipe velocity: {breakdown.pipe_velocity:.1f} m/s")
            else:
                breakdown.messages.append(f"Pipe velocity: {breakdown.pipe_velocity:.1f} m/s (good)")

            # Friction losses using simplified formula
            # ΔP (mbar) ≈ 0.5 * f * (L/D) * ρ * v²
            # For air at 20°C, ρ ≈ 1.2 kg/m³
            friction_factor = self.friction_factors.get('smooth', 0.025)
            air_density = 1.2  # kg/m³ at 20°C

            # Convert to mbar (1 Pa = 0.01 mbar)
            breakdown.pipe_friction_loss = (
                0.5 * friction_factor * (pipe_length / pipe_diameter_m) *
                air_density * breakdown.pipe_velocity ** 2 * 0.01
            )

            # Fitting losses
            if num_bends:
                k_total = num_bends * self.k_factors['90_bend']
                # Add entrance and exit losses
                k_total += self.k_factors['entrance'] + self.k_factors['exit']

                breakdown.fitting_losses = (
                    0.5 * k_total * air_density * breakdown.pipe_velocity ** 2 * 0.01
                )
                breakdown.messages.append(f"Fittings: {num_bends} × 90° bends + entrance/exit")
        else:
            # Default pipe losses if not specified
            breakdown.pipe_friction_loss = 15  # mbar
            breakdown.fitting_losses = 10  # mbar
            breakdown.messages.append("Using default pipe losses (25 mbar total)")

        # 4. DIFFUSER PRESSURE DROP
        if not diffuser_type:
            diffuser_type = app_data.get('default_diffuser', 'fine')
            breakdown.messages.append(f"Using default {diffuser_type} diffuser for {application}")

        breakdown.diffuser_loss = self.diffuser_pressures.get(diffuser_type, 100)

        # 5. CALCULATE TOTAL PRESSURE
        breakdown.subtotal_pressure = (
            breakdown.static_pressure +
            breakdown.pipe_friction_loss +
            breakdown.fitting_losses +
            breakdown.diffuser_loss
        )

        # Handle multiple tanks in series (additive pressure)
        if num_tanks > 1 and tank_config == 'series':
            breakdown.subtotal_pressure *= num_tanks
            breakdown.messages.append(f"Series tanks: Pressure × {num_tanks}")

        # Apply safety factor
        breakdown.safety_margin = breakdown.subtotal_pressure * (breakdown.safety_factor - 1)
        breakdown.total_pressure = breakdown.subtotal_pressure + breakdown.safety_margin

        # 6. ALTITUDE CORRECTIONS
        if altitude > 0:
            # Pressure correction: +1% per 100m
            pressure_correction = 1 + (altitude / 100 / 100)  # altitude/100 gives percentage
            breakdown.altitude_corrected_pressure = breakdown.total_pressure * pressure_correction

            # Flow correction: slightly less effect
            flow_correction = 1 + (altitude / 120 / 100)  # slightly less than pressure correction
            breakdown.corrected_airflow_m3_hr = breakdown.base_airflow_m3_hr * flow_correction

            breakdown.altitude_correction = pressure_correction
            breakdown.messages.append(f"Altitude correction at {altitude}m: +{(pressure_correction-1)*100:.1f}%")
        else:
            breakdown.altitude_corrected_pressure = breakdown.total_pressure
            breakdown.corrected_airflow_m3_hr = breakdown.base_airflow_m3_hr

        # 7. POWER ESTIMATION
        # Power (kW) = (Q × P) / (36000 × η)
        efficiency = 0.5  # Typical side channel blower efficiency
        power_kw = (breakdown.corrected_airflow_m3_hr * breakdown.altitude_corrected_pressure) / (36000 * efficiency)

        # Check limits and add warnings
        if breakdown.altitude_corrected_pressure > 800:
            breakdown.warnings.append("High pressure (>800 mbar) - special blower or multistage required")
        if breakdown.altitude_corrected_pressure > 1000:
            breakdown.warnings.append("Very high pressure (>1000 mbar) - consider positive displacement blower")

        # Prepare return dictionary
        return {
            'airflow_m3_min': breakdown.base_airflow_m3_min,
            'airflow_m3_hr': breakdown.corrected_airflow_m3_hr,
            'pressure_mbar': breakdown.altitude_corrected_pressure,
            'power_kw': power_kw,
            'breakdown': {
                'base_airflow_m3_min': round(breakdown.base_airflow_m3_min, 3),
                'base_airflow_m3_hr': round(breakdown.base_airflow_m3_hr, 1),
                'corrected_airflow_m3_hr': round(breakdown.corrected_airflow_m3_hr, 1),
                'static_pressure': round(breakdown.static_pressure, 1),
                'pipe_friction': round(breakdown.pipe_friction_loss, 1),
                'fitting_losses': round(breakdown.fitting_losses, 1),
                'diffuser_loss': round(breakdown.diffuser_loss, 1),
                'subtotal_pressure': round(breakdown.subtotal_pressure, 1),
                'safety_margin': round(breakdown.safety_margin, 1),
                'total_pressure': round(breakdown.total_pressure, 1),
                'final_pressure': round(breakdown.altitude_corrected_pressure, 1),
                'pipe_velocity': round(breakdown.pipe_velocity, 1) if breakdown.pipe_velocity else None,
                'altitude_correction': round(breakdown.altitude_correction, 3),
                'safety_factor': breakdown.safety_factor,
                'specific_gravity': breakdown.specific_gravity
            },
            'tank_info': {
                'area_m2': round(tank_area, 1),
                'volume_m3': round(tank_volume, 1),
                'depth_m': tank_depth,
                'num_tanks': num_tanks,
                'configuration': tank_config
            },
            'messages': breakdown.messages,
            'warnings': breakdown.warnings
        }


# Test the calculator
if __name__ == "__main__":
    calculator = EnhancedBlowerCalculator()

    # Test case: Waste water treatment plant
    print("Test Case: Waste Water Treatment")
    print("-" * 40)

    result = calculator.calculate(
        tank_length=6,
        tank_width=3,
        tank_depth=2,
        application='waste_water',
        altitude=1420,  # Johannesburg
        pipe_diameter=100,
        pipe_length=50,
        num_bends=4,
        diffuser_type='fine'
    )

    print(f"Airflow Required: {result['airflow_m3_hr']:.1f} m³/hr")
    print(f"Pressure Required: {result['pressure_mbar']:.1f} mbar")
    print(f"Estimated Power: {result['power_kw']:.1f} kW")
    print("\nBreakdown:")
    for key, value in result['breakdown'].items():
        if value is not None:
            print(f"  {key}: {value}")
    print("\nMessages:")
    for msg in result['messages']:
        print(f"  - {msg}")
    if result['warnings']:
        print("\nWarnings:")
        for warn in result['warnings']:
            print(f"  ⚠ {warn}")