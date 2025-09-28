"""
Comprehensive Blower Selection Calculator
==========================================
Integrates all calculation modules: base requirements, altitude/temperature
corrections, application factors, and multiple blower configurations.

Author: Liberlocus for Crelec S.A.
Date: September 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import math
from datetime import datetime

# Import our modules
from location_handler import LocationHandler, LocationData
from blower_configuration import BlowerConfigurationOptimizer, BlowerConfiguration


@dataclass
class CalculationInputs:
    """All user inputs for calculation"""
    # Operation type
    operation_type: str = 'compression'  # 'compression' or 'vacuum'

    # Tank dimensions
    tank_length: float  # meters
    tank_width: float   # meters
    tank_depth: float   # meters (water depth)
    num_tanks: int = 1
    tank_config: str = 'parallel'  # 'parallel' or 'series'

    # Location/Environment
    location_text: str = ''  # Free text for location
    altitude: Optional[float] = None  # meters, can be extracted from location
    temperature: Optional[float] = None  # °C, can be extracted from location

    # Application
    application_type: str = 'waste_water'  # 'waste_water', 'fish_hatchery', 'industrial'
    specific_application: Optional[str] = None  # e.g., 'activated_sludge', 'trout_farm'

    # Pipe system
    pipe_length: float = 50  # meters
    pipe_diameter: float = 100  # mm
    num_bends: int = 4

    # Diffuser system
    diffuser_type: str = 'fine_bubble'  # 'fine_bubble', 'coarse_bubble', 'jet'
    diffuser_depth: Optional[float] = None  # If None, use tank_depth

    # Optional overrides
    safety_factor: Optional[float] = None  # Override automatic safety factor
    fouling_factor: Optional[float] = None  # Override automatic fouling factor


@dataclass
class CalculationResults:
    """Complete calculation results with all details"""
    # Basic results
    base_airflow: float  # m³/hr before corrections
    base_pressure: float  # mbar before corrections

    # Corrected requirements
    required_airflow: float  # m³/hr after all corrections
    required_pressure: float  # mbar after all corrections

    # Breakdown of calculations
    tank_volume: float
    oxygen_demand: float  # kg O2/hr
    static_pressure: float  # mbar
    pipe_losses: float  # mbar
    diffuser_losses: float  # mbar

    # Correction factors applied
    altitude_correction: float
    temperature_correction: float
    application_factor: float
    safety_factor: float
    fouling_factor: float

    # Location data
    location_data: LocationData

    # Configuration options
    configurations: List[BlowerConfiguration]
    recommended_config: BlowerConfiguration

    # Comparison table data
    comparison_table: List[Dict]

    # Energy analysis
    annual_energy_base: float  # kWh/year for single blower
    annual_energy_optimized: float  # kWh/year for recommended config
    annual_savings_kwh: float
    annual_savings_currency: float  # Rands
    payback_months: float

    # Messages and notes
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ComprehensiveBlowerCalculator:
    """
    Main calculator that orchestrates all calculation modules
    """

    def __init__(self):
        self.location_handler = LocationHandler()
        self.config_optimizer = BlowerConfigurationOptimizer()

        # Application-specific parameters
        self.application_params = {
            'waste_water': {
                'oxygen_transfer_efficiency': 0.20,  # 20% SOTE for fine bubble
                'alpha_factor': 0.65,  # O2 transfer in wastewater vs clean water
                'beta_factor': 0.95,  # O2 saturation in wastewater vs clean water
                'safety_factor': 1.2,
                'fouling_factor': 1.5,
                'diffuser_pressure': 150,  # mbar for fine bubble
                'turnover_rate': 2.0,  # tank volumes per hour
                'load_profile': {  # Typical diurnal pattern
                    'night': 0.3,
                    'early_morning': 0.4,
                    'morning_peak': 1.2,
                    'midday': 0.8,
                    'afternoon': 0.9,
                    'evening_peak': 1.1,
                    'late_evening': 0.5
                }
            },
            'fish_hatchery': {
                'oxygen_transfer_efficiency': 0.10,  # 10% SOTE for coarse bubble
                'alpha_factor': 0.90,  # Cleaner water
                'beta_factor': 0.98,
                'safety_factor': 1.5,  # Higher safety for living creatures
                'fouling_factor': 1.2,  # Less fouling
                'diffuser_pressure': 80,  # mbar for coarse bubble
                'turnover_rate': 1.0,
                'load_profile': {  # More constant
                    'night': 0.7,
                    'morning': 0.9,
                    'feeding_time': 1.3,
                    'afternoon': 1.0,
                    'evening': 0.8
                }
            },
            'industrial': {
                'oxygen_transfer_efficiency': 0.15,
                'alpha_factor': 0.75,
                'beta_factor': 0.95,
                'safety_factor': 1.15,
                'fouling_factor': 1.3,
                'diffuser_pressure': 100,
                'turnover_rate': 1.5,
                'load_profile': {  # Production hours
                    'night': 0.1,
                    'shift1': 1.0,
                    'shift2': 1.0,
                    'shift3': 0.5
                }
            }
        }

        # Electricity cost (R/kWh)
        self.electricity_cost = 2.50  # South African average industrial rate

    def calculate(self, inputs: CalculationInputs) -> CalculationResults:
        """
        Main calculation method that orchestrates all modules
        """
        # Step 1: Process location for altitude/temperature
        location_data = self.location_handler.process_location_input(inputs.location_text)

        # Override with explicit values if provided
        if inputs.altitude is not None:
            location_data.altitude = inputs.altitude
            location_data.altitude_source = 'user'
        if inputs.temperature is not None:
            location_data.temperature = inputs.temperature
            location_data.temp_source = 'user'

        # Step 2: Calculate base requirements
        base_airflow, oxygen_demand = self._calculate_base_airflow(inputs)
        base_pressure, static_p, pipe_p, diff_p = self._calculate_base_pressure(inputs)

        # Step 3: Get application parameters
        app_params = self.application_params[inputs.application_type]
        safety_factor = inputs.safety_factor or app_params['safety_factor']
        fouling_factor = inputs.fouling_factor or app_params['fouling_factor']

        # Step 4: Calculate correction factors
        corrections = self.location_handler.calculate_correction_factors(
            location_data.altitude,
            location_data.temperature
        )

        # Step 5: Apply all corrections
        # Airflow corrections (volumetric flow stays same, mass flow changes)
        corrected_airflow = base_airflow * safety_factor * fouling_factor

        # Pressure corrections (altitude reduces available pressure)
        altitude_pressure_factor = 1 / corrections['pressure_correction'] if corrections['pressure_correction'] < 1 else 1.0
        corrected_pressure = base_pressure * altitude_pressure_factor * fouling_factor

        # Step 6: Generate blower configurations
        configurations = self.config_optimizer.calculate_configurations(
            corrected_airflow,
            corrected_pressure,
            inputs.application_type,
            app_params['load_profile']
        )

        recommended_config = configurations[0]  # Top scored

        # Step 7: Generate comparison table
        comparison_table = self._generate_comparison_table(
            configurations,
            corrected_airflow,
            corrected_pressure
        )

        # Step 8: Calculate energy and cost analysis
        energy_analysis = self._calculate_energy_analysis(
            corrected_airflow,
            corrected_pressure,
            configurations,
            app_params['load_profile']
        )

        # Step 9: Generate messages and warnings
        messages = []
        warnings = []

        messages.append(location_data.message)
        messages.append(f"Application: {inputs.application_type.replace('_', ' ').title()}")
        messages.append(f"Base requirements: {base_airflow:.0f} m³/hr @ {base_pressure:.0f} mbar")
        messages.append(f"After corrections: {corrected_airflow:.0f} m³/hr @ {corrected_pressure:.0f} mbar")

        if corrections['pressure_correction'] < 0.85:
            warnings.append(f"⚠️ High altitude ({location_data.altitude}m) significantly affects blower performance")

        if fouling_factor > 1.3:
            warnings.append(f"⚠️ High fouling factor ({fouling_factor}) - regular maintenance critical")

        # Compile results
        return CalculationResults(
            base_airflow=base_airflow,
            base_pressure=base_pressure,
            required_airflow=corrected_airflow,
            required_pressure=corrected_pressure,
            tank_volume=inputs.tank_length * inputs.tank_width * inputs.tank_depth * inputs.num_tanks,
            oxygen_demand=oxygen_demand,
            static_pressure=static_p,
            pipe_losses=pipe_p,
            diffuser_losses=diff_p,
            altitude_correction=corrections['pressure_correction'],
            temperature_correction=corrections['temperature_ratio'],
            application_factor=app_params['safety_factor'],
            safety_factor=safety_factor,
            fouling_factor=fouling_factor,
            location_data=location_data,
            configurations=configurations,
            recommended_config=recommended_config,
            comparison_table=comparison_table,
            annual_energy_base=energy_analysis['base'],
            annual_energy_optimized=energy_analysis['optimized'],
            annual_savings_kwh=energy_analysis['savings_kwh'],
            annual_savings_currency=energy_analysis['savings_rand'],
            payback_months=energy_analysis['payback_months'],
            messages=messages,
            warnings=warnings
        )

    def _calculate_base_airflow(self, inputs: CalculationInputs) -> Tuple[float, float]:
        """Calculate base airflow requirement"""
        app_params = self.application_params[inputs.application_type]

        # Tank volume
        tank_volume = inputs.tank_length * inputs.tank_width * inputs.tank_depth
        total_volume = tank_volume * inputs.num_tanks

        # Application-specific oxygen demand (kg O2/hr)
        if inputs.application_type == 'waste_water':
            # Typical: 2 kg O2/kg BOD, 150 mg/L BOD, 2 turnovers/hr
            bod_load = 0.150 * total_volume * app_params['turnover_rate']  # kg/hr
            oxygen_demand = bod_load * 2.0  # kg O2/hr
        elif inputs.application_type == 'fish_hatchery':
            # Typical: 0.4 kg O2/kg feed, 2% body weight feeding
            biomass = total_volume * 30  # kg/m³ typical stocking density
            feed_rate = biomass * 0.02 / 24  # kg/hr
            oxygen_demand = feed_rate * 0.4
        else:
            # Industrial - generic
            oxygen_demand = total_volume * 0.5  # kg O2/hr/m³

        # Air contains 0.28 kg O2/m³ at standard conditions
        # Account for oxygen transfer efficiency and alpha factor
        air_required = oxygen_demand / (0.28 * app_params['oxygen_transfer_efficiency'] * app_params['alpha_factor'])

        # Convert to m³/hr
        base_airflow = air_required

        return base_airflow, oxygen_demand

    def _calculate_base_pressure(self, inputs: CalculationInputs) -> Tuple[float, float, float, float]:
        """Calculate base pressure requirement"""
        app_params = self.application_params[inputs.application_type]

        # Static pressure (hydrostatic)
        diffuser_depth = inputs.diffuser_depth or inputs.tank_depth
        static_pressure = diffuser_depth * 98.1  # mbar/m

        # Pipe friction losses (simplified Darcy-Weisbach)
        # Velocity = Flow / Area
        pipe_area = math.pi * (inputs.pipe_diameter / 2000) ** 2  # m²
        velocity = (self._calculate_base_airflow(inputs)[0] / 3600) / pipe_area  # m/s

        # Friction factor (approximate for turbulent flow)
        reynolds = velocity * (inputs.pipe_diameter / 1000) * 1.2 / 0.000015  # Air at 20°C
        friction_factor = 0.02 if reynolds > 4000 else 0.04

        # Pipe losses
        pipe_losses = friction_factor * (inputs.pipe_length / (inputs.pipe_diameter / 1000)) * (1.2 * velocity ** 2) / 2 / 100

        # Fitting losses (each 90° bend ~= 30 pipe diameters)
        fitting_losses = inputs.num_bends * 30 * friction_factor * (1.2 * velocity ** 2) / 2 / 100

        total_pipe_losses = pipe_losses + fitting_losses

        # Diffuser losses
        diffuser_losses = app_params['diffuser_pressure']

        # Total pressure
        base_pressure = static_pressure + total_pipe_losses + diffuser_losses

        return base_pressure, static_pressure, total_pipe_losses, diffuser_losses

    def _generate_comparison_table(self, configs: List[BlowerConfiguration],
                                  airflow: float, pressure: float) -> List[Dict]:
        """Generate comparison table data for display"""
        table_data = []

        # Add single blower baseline
        table_data.append({
            'configuration': 'Single Blower',
            'num_blowers': '1×',
            'size_each': f"{airflow:.0f} m³/hr",
            'pressure_each': f"{pressure:.0f} mbar",
            'energy_savings': 'BASELINE',
            'turndown_range': '50-100%',
            'redundancy': 'None',
            'relative_cost': '1.0×',
            'recommended': False,
            'notes': 'Simple, no redundancy'
        })

        # Add configuration options
        for config in configs[:4]:  # Top 4 options
            is_recommended = (config == configs[0])  # First is best scored

            if config.config_type == 'duty_standby':
                config_name = 'Duty/Standby'
            elif config.config_type == 'parallel':
                config_name = f'Parallel {config.num_blowers}×'
            else:
                config_name = config.config_type.title()

            table_data.append({
                'configuration': config_name,
                'num_blowers': f"{config.num_blowers}×",
                'size_each': f"{config.individual_capacity:.0f} m³/hr",
                'pressure_each': f"{config.individual_pressure:.0f} mbar",
                'energy_savings': f"{config.energy_savings:.0f}% SAVINGS" if config.energy_savings > 0 else "No savings",
                'turndown_range': f"{config.turndown_range[0]:.0f}-{config.turndown_range[1]:.0f}%",
                'redundancy': f"N+{config.num_standby}" if config.num_standby > 0 else "None",
                'relative_cost': f"{config.capital_cost_factor:.1f}×",
                'recommended': is_recommended,
                'notes': config.recommendation
            })

        return table_data

    def _calculate_energy_analysis(self, airflow: float, pressure: float,
                                  configs: List[BlowerConfiguration],
                                  load_profile: Dict) -> Dict:
        """Calculate detailed energy and cost analysis"""

        # Baseline: single blower power consumption
        # Power (kW) = (Q × P) / (36000 × η)
        # Q in m³/hr, P in mbar, η = efficiency (typically 0.7)
        baseline_power = (airflow * pressure) / (36000 * 0.7)  # kW

        # Annual baseline (weighted by load profile)
        annual_hours = 8760
        hours_per_period = annual_hours / len(load_profile)

        baseline_annual = 0
        for period, load in load_profile.items():
            # Power varies with cube of speed (load)
            period_power = baseline_power * (load ** 3)
            baseline_annual += period_power * hours_per_period

        # Optimized: recommended configuration
        recommended = configs[0]
        optimized_annual = baseline_annual * (1 - recommended.energy_savings / 100)

        # Savings
        savings_kwh = baseline_annual - optimized_annual
        savings_rand = savings_kwh * self.electricity_cost

        # Payback calculation
        # Additional capital cost
        additional_capital = (recommended.capital_cost_factor - 1) * 50000  # Assume R50k base
        payback_months = (additional_capital / savings_rand) * 12 if savings_rand > 0 else 999

        return {
            'base': baseline_annual,
            'optimized': optimized_annual,
            'savings_kwh': savings_kwh,
            'savings_rand': savings_rand,
            'payback_months': payback_months
        }

    def format_comparison_table_text(self, table_data: List[Dict]) -> str:
        """Format comparison table for text display"""
        lines = []
        lines.append("=" * 80)
        lines.append("BLOWER CONFIGURATION COMPARISON")
        lines.append("=" * 80)
        lines.append(f"{'Configuration':<20} {'Blowers':<10} {'Size Each':<15} {'Energy':<15} {'Redundancy':<12}")
        lines.append("-" * 80)

        for row in table_data:
            prefix = "⭐ " if row['recommended'] else "   "
            lines.append(
                f"{prefix}{row['configuration']:<17} "
                f"{row['num_blowers']:<10} "
                f"{row['size_each']:<15} "
                f"{row['energy_savings']:<15} "
                f"{row['redundancy']:<12}"
            )

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    calculator = ComprehensiveBlowerCalculator()

    # Example inputs
    inputs = CalculationInputs(
        tank_length=6.0,
        tank_width=3.0,
        tank_depth=2.0,
        num_tanks=3,
        tank_config='parallel',
        location_text="Johannesburg",
        application_type='waste_water',
        pipe_length=100,
        pipe_diameter=150,
        num_bends=6,
        diffuser_type='fine_bubble'
    )

    # Calculate
    results = calculator.calculate(inputs)

    # Display results
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BLOWER SELECTION CALCULATION")
    print("=" * 80)

    print(f"\n📍 Location Analysis:")
    for msg in results.messages:
        print(f"   {msg}")

    print(f"\n📊 Requirements Summary:")
    print(f"   Tank Volume: {results.tank_volume:.0f} m³")
    print(f"   Oxygen Demand: {results.oxygen_demand:.1f} kg O2/hr")
    print(f"   Base Airflow: {results.base_airflow:.0f} m³/hr")
    print(f"   Base Pressure: {results.base_pressure:.0f} mbar")
    print(f"   After Corrections: {results.required_airflow:.0f} m³/hr @ {results.required_pressure:.0f} mbar")

    print(f"\n" + calculator.format_comparison_table_text(results.comparison_table))

    print(f"\n💰 Energy & Cost Analysis:")
    print(f"   Annual Energy (Single Blower): {results.annual_energy_base:.0f} kWh")
    print(f"   Annual Energy (Recommended): {results.annual_energy_optimized:.0f} kWh")
    print(f"   Annual Savings: {results.annual_savings_kwh:.0f} kWh = R{results.annual_savings_currency:,.0f}")
    print(f"   Payback Period: {results.payback_months:.0f} months")

    print(f"\n✅ RECOMMENDATION:")
    print(f"   {results.recommended_config.config_type.upper()} configuration")
    print(f"   {results.recommended_config.num_blowers} × {results.recommended_config.individual_capacity:.0f} m³/hr blowers")
    print(f"   {results.recommended_config.recommendation}")

    if results.warnings:
        print(f"\n⚠️ Warnings:")
        for warning in results.warnings:
            print(f"   {warning}")