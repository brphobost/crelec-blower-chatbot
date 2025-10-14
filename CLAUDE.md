# Crelec Blower Selection Chatbot - Development Documentation

## Project Overview
An intelligent chatbot system for Crelec S.A. that helps end-users select the right blower for their applications through a conversational interface. The system features **professional-grade engineering calculations** including pipe losses, diffuser selection, environment factors, and multiple tank configurations.

## Current Version: v2.1.0 (October 2024)
- **Live URL**: https://blower-chatbot.vercel.app
- **Repository**: https://github.com/brphobost/crelec-blower-chatbot
- **Deployment**: Vercel (auto-deploys from GitHub)
- **Status**: Production-ready with professional calculations
- **Achievement**: Quote generation reduced from 30 min to 2 min ✅

## ✅ Current Features (v2.1.0)

### 1. **Professional Calculation Engine**
- **Enhanced Calculator Module** (`enhanced_calculator.py`)
  - Pipe friction losses using Darcy-Weisbach formula
  - Fitting losses with K-factors for 90° bends
  - Diffuser pressure drop tables (fine/coarse/disc/tube)
  - Multiple tank configurations (series/parallel)
  - Environment factor adjustments (10-25% safety increase)
  - Altitude corrections for South African locations
  - Detailed calculation breakdown with all components
  - Pipe velocity validation and warnings

### 2. **Comprehensive Application Support** (v2.1.0)
Now supports 12 application types matching Crelec's professional form:
1. Waste Water Treatment
2. Fertiliser Production
3. Dental Aspiration
4. Sauna Systems
5. Aquaponics/Fish Farming
6. Bottling Lines
7. Pneumatic Conveying
8. Plastic Mold Processing
9. Metal Treatment Baths
10. Gas/Air Circulation
11. Materials Handling
12. Other (custom entry)

### 3. **Environment Conditions** (v2.1.0)
Operating environment selection with safety factors:
- **Normal** - Standard conditions (no adjustment)
- **Wet/Humid** - +10% safety factor
- **Dusty** - +15% safety factor
- **Coastal/Marine** - +20% safety factor
- **Gas/Chemical** - +25% safety factor
- **Extreme Climate** - +15% safety factor

### 4. **Enhanced Conversational Flow**
Professional data collection sequence:
1. **Operation type** - Compression/Vacuum
2. **Altitude** - Location with smart detection
3. **Application** - 12 types with numbered selection (1-12)
4. **Environment** - 6 conditions with numbered selection (1-6)
5. **Tank configuration** - Number of tanks, series/parallel
6. **Tank dimensions** - Visual guide with PNG image
7. **Pipe system** - Diameter, length, bends
8. **Diffuser type** - Fine bubble, disc, coarse, tube
9. **Email** - Quote delivery

### 5. **User Interface Improvements** (v2.0.4-v2.0.5)
- **Tank dimension image** - Visual PNG guide for measurements
- **Increased chat height** - 25% more space (625px desktop, 500px mobile)
- **Compact line spacing** - 30% reduction for more content visibility
- **Company links** - Crelec logo → crelec.co.za, Liberlocus → liberlocus.com
- **Version indicator** - Visible version number for deployment tracking
- **Markdown image support** - Proper rendering of images in chat

### 6. **Smart Product Matching**
- Database of real Crelec blower products
- Scoring algorithm considering capacity match and stock status
- Returns top 3 matched products
- Google Sheets integration for live catalog updates

### 7. **Professional PDF Quote Generation**
- Company branding with logos
- Unique quote ID with timestamp
- Detailed calculation breakdown
- Product recommendations with specifications
- 30-day validity period
- Contact information

### 8. **State Management & Architecture**
- **Stateless operation** for Vercel serverless functions
- **Client-side state tracking** for conversation continuity
- **Fallback calculator** for resilience
- **CORS headers** properly configured
- **HTTP protocol** compliance

## 🔧 Technical Stack

### Frontend
- HTML/CSS/JavaScript (vanilla)
- jsPDF for PDF generation
- Client-side state management
- Responsive design (mobile-first)
- Markdown rendering support

### Backend
- Python serverless functions (Vercel)
- Enhanced calculator with engineering formulas
- SQLite for quote storage
- JSON product database

### Infrastructure
- GitHub repository (version control)
- Vercel hosting (auto-deployment)
- Free tier services (zero monthly costs)

## 🎯 Key Technical Achievements

### 1. **Engineering Calculations**
- Industry-standard formulas from manufacturer specifications
- Waste Water: Q = Tank Area × 0.25 m³/min
- Fish Farming: Q = Pond Area × 0.002 m³/min
- Pressure = Static Head + Pipe Losses + Diffuser Loss + Corrections
- Environment and altitude factors properly applied

### 2. **Stateless Architecture Solution**
- **Problem**: Vercel serverless functions don't maintain memory
- **Solution**: Client tracks state, sends with each request
- **Result**: Reliable conversation flow without server-side sessions

### 3. **User Experience Optimizations**
- Numbered input options for faster selection
- Smart defaults based on application type
- Progressive disclosure of complex options
- Visual aids for tank dimensions
- Clear breakdown of all calculations

## 📊 Calculation Formulas

### Base Airflow Calculations
```python
# Waste Water Treatment
airflow_m3_min = tank_area * 0.25

# Fish Farming/Aquaponics
airflow_m3_min = tank_area * 0.002

# Industrial/Other
airflow_m3_min = (tank_volume * air_changes_per_hour) / 60
```

### Pressure Calculations
```python
# Total Pressure = Base Components + Corrections
static_pressure = depth * 98.1 * specific_gravity
pipe_friction = 0.5 * f * (L/D) * density * velocity^2 * 0.01
fitting_losses = 0.5 * k_total * density * velocity^2 * 0.01
diffuser_loss = 50-250 mbar (depending on type)

# Corrections
altitude_correction = 1 + (altitude_m / 10000)  # 1% per 100m
environment_factor = 1.0 to 1.25  # Based on conditions

total_pressure = (base_pressure + losses) * altitude_correction * environment_factor
```

## 🚀 Quick Start for Developers

### Project Structure
```
blower-chatbot/
├── api/                          # Vercel serverless functions
│   ├── chat.py                  # Main chat handler (PRODUCTION)
│   ├── enhanced_calculator.py   # Calculation engine
│   └── send_email.py            # Email handling
├── backend/                      # Development modules
│   ├── app.py                   # Local dev server
│   └── comprehensive_calculator.py
├── frontend/                     # User interface
│   ├── index.html               # Main chat interface
│   ├── chat.js                  # Client-side logic
│   ├── styles.css               # Styling
│   ├── quote-generator.js       # PDF generation
│   └── assets/
│       └── images/
│           └── tank-dimensions.png  # Visual guides
├── CLAUDE.md                     # This documentation
├── CALCULATIONS.md               # Formula documentation
└── vercel.json                   # Deployment config
```

### Local Development
```bash
# Backend development server
cd backend
python app.py  # Runs on http://localhost:8000

# Frontend development server
cd frontend
python -m http.server 8080  # Runs on http://localhost:8080
```

### Deployment Process
```bash
# 1. Make changes
# 2. Update version numbers in:
#    - CLAUDE.md (line 6)
#    - frontend/index.html (version indicator)
#    - frontend/widget.html (version indicator)

# 3. Commit and push
git add .
git commit -m "Description of changes"
git push origin master

# Auto-deploys to Vercel within 1-2 minutes
```

## 📈 Recent Updates & Changelog

### v2.1.0 (Oct 14, 2024) - MAJOR ENHANCEMENT
**Expanded Applications & Environment Factors**
- **NEW**: 12 application types (up from 3) matching Crelec form
- **NEW**: Environment condition question with 6 options
- **NEW**: Environment safety factors (10-25% increase)
- **NEW**: Numbered selection for both applications and environment
- **IMPROVED**: Reduced line spacing by 30% for compact display
- **UPDATE**: Environment factor shown in calculation breakdown

### v2.0.5 (Oct 14, 2024)
**UI Improvements**
- Increased chat box height by 25%
- Added clickable links to company logos
- Changed tagline to "2 minutes"
- CSS improvements for link styling

### v2.0.4 (Oct 14, 2024)
**Image Rendering Fix**
- Fixed markdown image to HTML conversion
- Images now render properly in chat
- Tank dimensions PNG displays correctly

### v2.0.3 (Oct 14, 2024)
**Altitude & Image Support**
- Fixed altitude correction calculations
- Created assets/images folder structure
- Tank dimension image support added

### v2.0.2 (Oct 14, 2024)
**Bug Fixes**
- Sea level now correctly sets 0m altitude
- Altitude correction formula fixed
- Added visual tank dimension guide

### v2.0.1 (Oct 14, 2024)
**State Management Fix**
- Fixed state updates between conversation steps
- Email quote generation properly triggers
- PDF generation working correctly

### v2.0.0 (Oct 14, 2024)
**Professional Calculations Release**
- Enhanced calculator implementation
- Multiple tank configurations
- Pipe system calculations
- Diffuser selection

## ⚠️ Important Architecture Notes

### Vercel Deployment Structure
- `/api/chat.py` - **PRODUCTION** endpoint (runs on Vercel)
- `/backend/app.py` - Development server only
- Always update BOTH when changing logic during development

### Critical Files for Updates
1. **Chat Flow**: `/api/chat.py`
2. **Calculations**: `/api/enhanced_calculator.py`
3. **Frontend Logic**: `/frontend/chat.js`
4. **Styling**: `/frontend/styles.css`

### Version Management
When making changes, update version in:
1. `CLAUDE.md` - Line 6
2. `frontend/index.html` - Version indicator div
3. `frontend/widget.html` - Version indicator div

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### 1. "500 Internal Server Error"
- **Cause**: HTTP headers sent before response status
- **Fix**: Ensure `send_response(200)` comes before headers

#### 2. Conversation Stuck
- **Cause**: State not updating properly
- **Fix**: Check client-side state management in chat.js

#### 3. Images Not Displaying
- **Cause**: Markdown not converted to HTML
- **Fix**: formatBotMessage() must handle image syntax

#### 4. Altitude Shows Wrong Value
- **Cause**: Default value applied incorrectly
- **Fix**: Check altitude parsing logic for "sea level"

#### 5. Environment Factor Not Applied
- **Cause**: Calculator not receiving environment_factor
- **Fix**: Ensure parameter passed to calculate()

## 🤝 Contact & Support

### Customer
- **Company**: Crelec S.A.
- **Website**: https://crelec.co.za
- **Email**: crelec@live.co.za

### Development
- **Developer**: Liberlocus
- **Website**: https://www.liberlocus.com
- **Project Manager**: Burak

## 📊 Success Metrics

### Achieved ✅
- Quote generation: 30 min → 2 min
- 24/7 availability
- Professional PDF documentation
- Lead capture on all inquiries

### Target Goals
- 50% reduction in admin workload
- 30% increase in quote-to-sale conversion
- Mobile platform expansion
- Full inventory integration

## 🔮 Future Enhancements

### Immediate Priorities
- [ ] Production email service setup
- [ ] Live inventory integration
- [ ] Admin dashboard for quotes
- [ ] WhatsApp Business API

### Long-term Vision
- [ ] Multi-language support
- [ ] AI-powered recommendations
- [ ] Payment gateway integration
- [ ] Predictive maintenance alerts

---

*Last Updated: October 14, 2024 - v2.1.0*
*Document maintained by Liberlocus Development Team*