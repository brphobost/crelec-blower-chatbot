# Blower Selection Calculations Documentation

## Overview
This document details all calculations, formulas, and assumptions used in the Crelec Blower Selection Chatbot. The formulas are based on manufacturer specifications from side channel blower brochures and industry standards.

## Core Calculation Formulas

### 1. Waste Water Treatment

**Airflow Calculation:**
```
Q = Tank Area (m²) × 0.25 m³/min
```
- Source: Manufacturer's application guide for waste water aeration
- Assumes: Activated sludge process with fine bubble diffusers
- Safety factor: Included in the 0.25 coefficient

**Pressure Calculation:**
```
P = Tank Depth (m) × Solution Specific Gravity × (1.2~1.5) mbar
```
- Specific gravity: 1.0 for clean water, 1.1 for waste water
- Factor 1.2-1.5 accounts for:
  - Hydrostatic pressure
  - Diffuser resistance
  - Pipe losses
  - Safety margin

### 2. Fish Hatchery/Aquaculture

**Airflow Calculation:**
```
Q = Pond Area (m²) × (0.0015~0.0025) m³/min
```
- We use middle value: 0.002 m³/min/m²
- Lower requirement due to:
  - Clean water (no BOD)
  - Fish only need dissolved oxygen maintenance
  - Gentle aeration to avoid stress

**Pressure Calculation:**
```
P = Pond Depth (m) × (1.2~1.5) mbar
```
- Similar to waste water but typically shallower installations
- Less diffuser resistance (coarse bubble typical)

### 3. Industrial Process

**Airflow Calculation:**
```
Q = Tank Volume (m³) × Air Changes per Hour / 60
```
- Default: 2 air changes per hour
- Varies widely by specific process
- User can override based on process requirements

**Pressure Calculation:**
```
P = Process Pressure + System Losses
```
- Process pressure: User-specified or estimated
- System losses: 50-150 mbar typical

## Pressure Component Breakdown

### Total Pressure Calculation
```
P_total = P_static + P_pipe + P_diffuser + P_safety
```

### Component Details

#### 1. Static Pressure (Hydrostatic)
```
P_static = Depth (m) × 98.1 mbar/m × Specific Gravity
```
- Water at 20°C: SG = 1.0
- Waste water: SG = 1.05-1.1
- Sea water: SG = 1.025

#### 2. Pipe Losses
```
P_pipe = P_friction + P_fittings
```

**Friction Losses (Darcy-Weisbach):**
```
ΔP = f × (L/D) × (ρ × v²)/2
```
Where:
- f = friction factor (0.02-0.03 for smooth pipes)
- L = pipe length (m)
- D = pipe diameter (m)
- ρ = air density (kg/m³)
- v = air velocity (m/s)

**Typical Values:**
- 50mm pipe, 50m length: ~20 mbar
- 100mm pipe, 50m length: ~10 mbar

**Fitting Losses:**
```
ΔP_fitting = K × (ρ × v²)/2
```
K factors:
- 90° elbow: K = 0.9
- 45° elbow: K = 0.4
- Tee junction: K = 1.8
- Gate valve (open): K = 0.2

#### 3. Diffuser Pressure Drop

**Fine Bubble Diffusers:**
- Membrane type: 200-350 mbar
- Ceramic disc: 150-250 mbar
- Typical design: 250 mbar

**Coarse Bubble Diffusers:**
- Perforated pipe: 30-80 mbar
- Sparger: 50-100 mbar
- Typical design: 50 mbar

**Crelec Standard (from form):**
- 7×25mm galvanized pipes
- 2mm holes, 400mm apart
- Estimated pressure drop: 100-150 mbar

#### 4. Safety Factors

**By Application:**
- Waste Water: 1.2 (20% safety)
- Fish Farming: 1.5 (50% safety - critical application)
- Industrial: 1.3 (30% safety)

**Fouling Factors (long-term):**
- Fine bubble in waste water: 1.5-2.0
- Coarse bubble: 1.2-1.3
- Clean water: 1.1-1.2

## Altitude Corrections

### Pressure Correction
```
P_corrected = P_sea_level × (1 + Altitude/10000)
```
- Johannesburg (1750m): +17.5% pressure required
- Approximate: +1% per 100m elevation

### Flow Correction
```
Q_corrected = Q_sea_level × (1 + Altitude/12000)
```
- Less significant than pressure
- Johannesburg: +14.6% flow required

### Density Ratio
```
ρ_altitude / ρ_sea_level = exp(-Altitude/8500)
```
- Affects actual mass flow delivered

## Temperature Corrections

### Air Density
```
ρ = P / (R × T)
```
- R = 287 J/(kg·K) for air
- Affects mass flow rate

### Dissolved Oxygen Saturation
```
DO_sat = 14.6 - 0.4×T + 0.008×T²
```
- T in °C
- Affects oxygen transfer efficiency

### Correction Factor
```
θ = 1.024^(T-20)
```
- For biological activity rates
- Higher temp = higher metabolic rate

## Multiple Tank Configurations

### Series Connection
- Flow: Same through all tanks
- Pressure: Additive (P_total = ΣP_tanks)
- Use when: Different water depths

### Parallel Connection
- Flow: Divided (Q_each = Q_total/n)
- Pressure: Same for all (highest tank governs)
- Use when: Same water depths

## Energy Calculations

### Power Requirement
```
Power (kW) = (Q × P) / (36000 × η)
```
Where:
- Q = airflow (m³/hr)
- P = pressure (mbar)
- η = blower efficiency (0.4-0.6 typical)

### Annual Energy
```
Energy (kWh/year) = Power × Operating Hours × Load Factor
```
- Continuous: 8760 hours/year
- Load factor: 0.7-0.9 typical

### Multiple Blower Benefits
- Affinity laws: Power ∝ Speed³
- Running 2 blowers at 70% = 69% power of 1 at 100%
- Typical savings: 20-40% with VFD control

## Validation Ranges

### Input Validation
- Tank depth: 0.5-10m (typical 2-4m)
- Tank area: 1-1000m²
- Pipe diameter: 25-500mm
- Pipe length: 1-1000m
- Number of bends: 0-20
- Altitude: 0-3000m
- Temperature: 0-45°C

### Output Ranges
- Airflow: 0.1-10000 m³/hr
- Pressure: 50-1000 mbar
- Power: 0.1-100 kW

## Special Considerations

### Wet/Dusty Environments
- Wet: Add inlet filter, consider corrosion
- Dusty: Heavy-duty inlet filter required
- Sea/Coastal: Stainless steel or coated components
- Gas: Explosion-proof motors required

### Start-up Conditions
- Empty tank start: Lower initial pressure
- Gradual filling: Pressure increases linearly
- Consider bypass valve for start-up

### Turndown Requirements
- Minimum flow: 30-40% of design
- VFD control recommended
- Multiple blowers for flexibility

## References

1. Side Channel Blower Application Guide (Manufacturer documentation)
2. Metcalf & Eddy - Wastewater Engineering
3. ASCE Manual 108 - Pipeline Design for Water
4. EPA Fine Pore Aeration Systems
5. Aquaculture Engineering (Timmons & Ebeling)

## Revision History

- v1.0 (Oct 2024): Initial documentation
- Based on Crelec brochure formulas
- Validated against existing calculator

---

*Note: These calculations represent typical values. Actual requirements may vary based on specific site conditions, water chemistry, and process requirements. Always verify with detailed engineering calculations for critical applications.*