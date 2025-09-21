# Crelec Blower Selection Chatbot - Development Documentation

## Project Overview
An intelligent chatbot system for Crelec S.A. that helps end-users select the right blower for their applications through a conversational interface. The system calculates requirements based on user inputs, matches products from inventory, and generates professional PDF quotes.

## Current Version: v1.2.0
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
1. **Email Sending**: Currently only downloads PDF locally (EmailJS integration pending)
2. **Products Database**: Static JSON file (needs manual updates)
3. **Calculations**: Simplified model without:
   - Pipe friction losses
   - Multiple blower configurations (series/parallel)
   - Different tank geometries (only rectangular)
   - Temperature/humidity corrections
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

## 📈 Changelog

### v1.2.0 (Current - Sept 21, 2025)
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