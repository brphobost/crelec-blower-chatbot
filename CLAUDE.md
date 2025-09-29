# Crelec Blower Selection Chatbot - Development Documentation

## Project Overview
An intelligent chatbot system for Crelec S.A. that helps end-users select the right blower for their applications through a conversational interface. The system calculates requirements based on user inputs, matches products from inventory, and generates professional PDF quotes.

## Current Version: v1.6.5
- **Live URL**: https://blower-chatbot.vercel.app
- **Repository**: https://github.com/brphobost/crelec-blower-chatbot
- **Deployment**: Vercel (auto-deploys from GitHub)

## ✅ Completed Features (MVP)

### 1. **Core Calculation Engine**
- Simple tank volume calculations (L × W × H)
- Airflow requirement calculation with safety factor (1.2)
- Pressure calculation based on:
  - Water depth (hydrostatic pressure)
  - System losses (150 mbar default)
  - Altitude correction
- Power estimation based on flow and pressure

### 2. **Conversational Chat Interface**
- Progressive data collection flow:
  1. Tank dimensions input
  2. Altitude/location specification
  3. Application type selection (Waste Water, Fish Hatchery, Industrial)
  4. Email collection for quote delivery
- Session management with state machine
- Input validation and error handling
- Mobile-responsive design

### 3. **Smart Product Matching**
- Database of 8 real blower products with specifications
- Scoring algorithm that considers:
  - Perfect match (100 points)
  - Over-specified options (80 points)
  - Higher capacity alternatives (70 points)
  - Stock status bonuses
- Returns top 3 matched products

### 4. **PDF Quote Generation**
- Professional PDF layout with:
  - Company branding (Crelec logo)
  - Quote number and validity period (30 days)
  - Customer details
  - Requirements analysis
  - Recommended products with specifications
  - Pricing and stock status
  - Contact information
- Automatic download to user's device
- "Powered by Liberlocus" branding

### 5. **Deployment Infrastructure**
- GitHub repository for version control
- Vercel hosting with auto-deployment
- Free tier services (no monthly costs)
- Version indicator for deployment tracking

### 6. **Embeddable Widget**
- Can be embedded on any website
- Floating chat button option
- Iframe integration available
- Maintains full functionality

## 🚧 Known Issues / Limitations

### Current Limitations:
1. **Email Sending**: Using Resend API (temporary for testing, needs production setup)
2. **Products Database**: Static JSON file (needs manual updates)
3. **Calculations**: Basic model - see Advanced Calculator Development section below
4. **Admin Features**: No dashboard or analytics
5. **Stock Integration**: Manual stock status updates required

## 📋 Planned Enhancements

### Phase 1 - Immediate (Next Sprint)
- [ ] **EmailJS Integration**
  - Set up EmailJS account
  - Configure email templates
  - Send PDF as attachment
  - CC admin on all quotes

- [ ] **Complex Calculations**
  - Add pipe loss calculations (friction factors, Reynolds numbers)
  - Support cylinder/irregular tank shapes
  - Multiple blower configurations
  - Variable safety factors

### Phase 2 - Short Term
- [ ] **Admin Dashboard**
  - Quote history viewer
  - Customer interaction logs
  - Analytics (conversion rates, popular products)
  - Product management interface

- [ ] **Google Sheets Integration**
  - Sync products from existing spreadsheet
  - Update prices/stock automatically
  - Export quotes to sheets

### Phase 3 - Medium Term
- [ ] **Enhanced Intelligence**
  - GPT integration for natural language understanding
  - Auto-detect location for altitude
  - Suggest alternatives based on budget
  - Learn from successful quotes

- [ ] **CRM Features**
  - Customer profiles
  - Quote follow-up reminders
  - Sales pipeline tracking
  - Email marketing integration

### Phase 4 - Long Term
- [ ] **Advanced Features**
  - Multi-language support
  - WhatsApp Business integration
  - Payment gateway for instant purchases
  - AR visualization of blowers
  - Maintenance reminders for existing customers

## 🔧 Technical Stack

### Frontend
- HTML/CSS/JavaScript (vanilla)
- jsPDF for PDF generation
- EmailJS for email sending (pending)
- Responsive design with mobile support

### Backend
- Python with FastAPI (serverless functions)
- SQLite for data storage
- JSON for product database

### Infrastructure
- GitHub for version control
- Vercel for hosting and auto-deployment
- Free tier services throughout

## 🎯 Key Decisions & Learnings (Sept 28, 2025)

### 1. Multiple Blower Configurations = MASSIVE Energy Savings
- Discovered 51-91% energy savings possible with parallel configurations
- 3 small blowers use 83% less power than 1 large blower over daily cycle
- Affinity Laws: Power = Speed³ (cubic relationship is key!)
- Payback period often < 1 year from energy savings alone

### 2. Altitude Corrections Are Critical for SA
- Johannesburg (1750m) requires 26% larger blowers than sea level
- Created comprehensive SA cities database with altitudes
- Automatic correction factors prevent undersized equipment

### 3. Chat Flow Must Match Existing Forms
- Users expect familiar order from paper forms
- Changed to match exact Crelec form: Operation → Installation → Altitude → Application → Dimensions
- Progressive disclosure reduces cognitive load

### 4. Vercel Architecture Gotcha
- **LESSON LEARNED**: Vercel uses `/api/` folder for serverless functions
- `/api/chat.py` is production, `/backend/app.py` is development
- Must update BOTH files when changing logic
- Frontend can have fallback messages for resilience

### 5. Version Tracking Is Essential
- Added visible version number (bottom right) for deployment verification
- Helps identify caching issues immediately
- Update in 3 places: CLAUDE.md, index.html, widget.html

## 🔮 Next Priority Enhancements

### Immediate (High Impact)
1. **Display Configuration Comparison Table** in frontend
   - Show energy savings visually
   - Highlight recommended configuration
   - Include payback period

2. **Product Matching** to configurations
   - Map actual Crelec products to each configuration
   - Show 2×600m³/hr vs 1×1200m³/hr options

3. **PDF Quote Enhancement**
   - Include configuration comparison
   - Show energy savings calculations
   - Add installation type considerations

### Future Considerations
- Integration with Crelec's inventory system
- WhatsApp Business API for mobile users
- Historical quote tracking and follow-up

## ⚠️ IMPORTANT: VERSION MANAGEMENT

### When Making Changes:
**ALWAYS UPDATE VERSION NUMBERS** in these locations:
1. `CLAUDE.md` - Current Version section (line 6)
2. `frontend/index.html` - Version indicator (line 49)
3. `frontend/widget.html` - Version indicator (line 60)

### Version Numbering Scheme:
- **Major changes** (new features): v1.2.0 → v1.3.0
- **Minor updates** (improvements): v1.1.0 → v1.1.1
- **Bug fixes only**: v1.1.1 → v1.1.2

### Example:
```bash
# After making changes, update all three files:
# CLAUDE.md: ## Current Version: v1.1.2
# index.html: <div class="version-indicator">v1.1.2</div>
# widget.html: <div style="...">v1.1.2</div>
```

## 📝 Development Guidelines

### To Add New Products:
1. Edit `frontend/products.json`
2. Include all required fields (airflow_min/max, pressure_min/max, etc.)
3. Commit and push to GitHub
4. Auto-deploys to production

### To Update Calculations:
1. Modify `calculator.py` or `api/chat.py`
2. Test locally first
3. Update version number in HTML files
4. Commit with descriptive message

### Version Numbering:
- Major changes: v2.0.0
- New features: v1.1.0
- Bug fixes: v1.0.1

## 🤝 Contact & Support

### Customer Contact:
- **Company**: Crelec S.A.
- **Email**: crelec@live.co.za
- **Phone**: +27 11 444 4555
- **Website**: www.crelec.co.za

### Development:
- **Developer**: Liberlocus
- **Project Manager**: Burak

## 📊 Success Metrics

### Current Goals:
- Reduce quote generation time from 30 min to 2 min ✅
- Capture 100% of inquiries as leads ✅
- Provide instant 24/7 availability ✅
- Professional PDF documentation ✅

### Future Goals:
- 50% reduction in admin workload
- 30% increase in quote-to-sale conversion
- Expand to mobile messaging platforms
- Integration with existing business systems

## 🚀 Quick Commands

### Local Development:
```bash
# Backend
cd backend
python app.py

# Frontend
cd frontend
python -m http.server 8080
```

### Deployment:
```bash
git add .
git commit -m "Your message"
git push
# Auto-deploys to Vercel
```

### Manual Deploy:
```bash
vercel --prod
```

## 🔬 Advanced Calculator Development (In Progress)

### Research Findings - Industry Standard Calculations

#### 1. **Critical Parameters from Crelec Form**
The existing Crelec form captures essential data:
- **Tank geometry**: Multiple tanks, series/parallel configurations
- **Pipe specifications**: Diameter, length, 90° bends
- **Environmental factors**: Altitude, temperature
- **Diffuser type**: 7x25mm galvanized pipes, 2mm holes, 400mm apart
- **Application specifics**: Depth, water type (wet/dusty/sea/gas)

#### 2. **Industry-Standard Calculation Methods**

**Wastewater Treatment:**
```
Pressure Required = Static Head + Friction Losses + Diffuser Loss
- Static Head = Depth(m) × 98.1 mbar/m
- Friction Loss = f × (L/D) × (ρv²/2)
- Diffuser Loss = 50-150 mbar (fine bubble)
```

**Aquaculture/Fish Farming:**
```
Airflow = Pond Area(m²) × 0.0015-0.0025 m³/min
Pressure = Depth(m) × 98.1 + 20-50 mbar (diffuser)
Oxygen Transfer: 1.3 kg O2/kWh under standard conditions
```

#### 3. **Missing Elements from Current Simple Calculator**
- **Oxygen Transfer Efficiency (SOTE)**: 2-6% for coarse, 15-25% for fine bubble
- **Alpha Factor**: 0.4-0.8 for wastewater (O2 transfer efficiency vs clean water)
- **Beta Factor**: 0.9-0.98 (O2 solubility in wastewater vs clean water)
- **Temperature Correction**: θ^(T-20) factor for biological activity
- **Multiple Blower Interaction**: Parallel reduces pressure, series increases
- **Pipe Network Analysis**: Using Darcy-Weisbach equation
- **Diffuser Fouling Factor**: 1.5-2.0 over system lifetime

#### 4. **Manufacturer Specifications**
- **Goorui GHBH series**: 0-2400 m³/h, 0-1000 mbar
- **Performance curves**: Tested at 15°C, sea level
- **Altitude/temperature corrections**: Required for accurate selection
- **Sirocco models**: Similar range, different efficiency curves

### Implementation Progress

#### ✅ Completed Modules

##### 1. **Smart Location Handler** (`backend/location_handler.py`)
- Intelligent extraction of altitude/temperature from user input
- Database of 20+ South African cities with climate data
- Automatic altitude correction calculations
- Clear communication of assumptions
- Fallback strategies for missing data

**Key Features:**
- Pattern recognition: "1500m", "Johannesburg", "sea level"
- Fuzzy matching for city names and aliases
- Correction factor calculations (pressure, flow, power)
- User-friendly messages about impact

#### 🚧 Next Steps (Priority Order)

##### Phase 1: Core Calculator Engine
1. **Tank Geometry Module**
   - Rectangular, cylindrical, irregular shapes
   - Multiple tank configurations (series/parallel)
   - Volume and surface area calculations

2. **Pressure Calculation Module**
   - Static head (depth-based)
   - Pipe friction losses (Darcy-Weisbach)
   - Fitting losses (elbows, valves, tees)
   - Diffuser pressure drop database

3. **Flow Calculation Module**
   - Oxygen demand calculations
   - SOTE-based airflow requirements
   - Safety factors and turndown ratios

##### Phase 2: Advanced Features
4. **Pipe Network Solver**
   - Complex branching systems
   - Pressure drop distribution
   - Velocity checks for erosion

5. **Oxygen Transfer Module**
   - Alpha/Beta factor corrections
   - Temperature effects on DO saturation
   - Process-specific oxygen demands

6. **Blower Selection Logic**
   - Performance curve matching
   - Efficiency point optimization
   - Multiple blower configurations

##### Phase 3: Integration
7. **Product Matching Engine**
   - Goorui/Sirocco curve database
   - Operating point analysis
   - Efficiency and power calculations

8. **Validation and Testing**
   - Compare with Excel calculator
   - Industry standard verification
   - Edge case handling

### Calculator Architecture

```
User Input (Chat Interface)
    ↓
Location Handler (altitude/temp)
    ↓
Application Selector (wastewater/aquaculture/industrial)
    ↓
Tank Configuration Module
    ↓
Flow Requirements Calculator
    ↓
Pressure Requirements Calculator
    ↓
Correction Factors Application
    ↓
Blower Selection Engine
    ↓
Product Matching & Recommendations
    ↓
Quote Generation
```

### Technical Stack for Calculator
- **Python 3.8+** for calculation engine
- **NumPy** for numerical computations
- **SciPy** for optimization and curve fitting
- **Pandas** for data handling
- **Modular design** for easy testing and maintenance

---

## ⚠️ CRITICAL ARCHITECTURE NOTES

### Vercel Deployment Structure
**IMPORTANT**: Vercel uses `/api/chat.py` as the serverless function endpoint, NOT `/backend/app.py`!
- `/api/chat.py` - This is what runs on Vercel production
- `/backend/app.py` - Local development server only
- Always update BOTH when changing chat flow logic

### Current Chat Flow (v1.5.1)
Streamlined for faster quotes:
1. **Operation Type** → Compression or Vacuum
2. **Altitude** → Location/city with smart detection
3. **Application** → Waste Water, Fish Farm, Industrial
4. **Operational Data** → Tank dimensions
5. **Results** → Calculations with recommendations
6. **Email** → Quote delivery

## 🚀 Major Technical Achievements

### Advanced Modules Created (Sept 2025)
1. **location_handler.py** - Smart SA cities database with altitude/temperature
   - 20+ South African cities with climate data
   - Altitude correction calculations (e.g., Johannesburg needs 26% larger blowers)
   - Fuzzy matching for city names

2. **blower_configuration.py** - Multiple blower optimizer
   - Shows 51-91% energy savings potential
   - Parallel vs single configurations
   - Payback period calculations

3. **comprehensive_calculator.py** - Integrates all corrections
   - Altitude/temperature corrections
   - Application-specific factors
   - Multiple tank configurations
   - Energy optimization

4. **improved_chat_flow.py** - Better UX conversation flow
   - Progressive disclosure
   - Smart defaults
   - Multiple input methods

## 📈 Changelog

### v1.4.2 (Sept 28, 2025)
- **CRITICAL FIX**: Updated `/api/chat.py` (Vercel's actual endpoint)
- Fixed chat flow in production environment
- Proper state progression: Operation → Installation → Altitude → Application → Dimensions

### v1.4.1 (Sept 28, 2025)
- Fixed frontend initial greeting
- Hardcoded correct flow in frontend as fallback
- Version tracking improvements

### v1.4.0 (Sept 28, 2025)
- **Major Update: Complete Chat Flow Redesign**
- Follows exact Crelec form order: Operation → Installation → Altitude → Application → Operational Data
- Added compression/vacuum selection as first question
- Added installation type question (Self/Consultant)
- Integrated smart location handler with SA cities database
- Added multiple blower configuration optimizer (51-91% energy savings)
- Comprehensive calculator with all correction factors
- Fixed duplicate greetings and state progression issues

### v1.3.0-dev (In Development - Sept 21, 2025)
- **Advanced Calculator Development Started**
- Created smart location handler with SA cities database
- Implemented altitude/temperature correction calculations
- Research completed on industry-standard methods
- Documented calculation requirements and next steps

### v1.2.0 (Sept 21, 2025)
- **New Feature:** Quote database logging system
- All quotes automatically saved with full details
- Google Sheets integration for easy access
- Created DATABASE_SETUP.md documentation
- Quotes visible in Vercel dashboard logs

### v1.1.2 (Sept 21, 2025)
- Fixed escaped newline characters (\n) properly showing as line breaks
- Stopped automatic PDF download to user's computer
- PDF now only sent via email for better lead tracking

### v1.1.1 (Sept 21, 2025)
- Fixed newline characters (\n) showing as text in chat
- Removed "Download Quote Again" button for better lead tracking
- Switched from SendGrid to Resend for easier email testing
- Changed admin CC to developer email during testing
- Fixed PDF encoding issues (removed emojis)
- Added version management instructions

### v1.1.0
- Fixed API routing issue
- Enabled email collection
- Added product matching
- PDF generation working

### v1.0.2
- Improved version indicator visibility

### v1.0.1
- Added version indicator
- Header redesign with logos

### v1.0.0
- Initial MVP release
- Basic calculations
- Chat interface
- Simple product recommendations

---

*This document should be updated with each significant change to maintain accurate project status.*