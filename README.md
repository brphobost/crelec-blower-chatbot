# Crelec Blower Selection Chatbot

A web-based chatbot for helping customers select the right blower for their applications. Features progressive data collection, automatic calculations, and embeddable widget for website integration.

🚀 **Live Demo**: https://blower-chatbot.vercel.app/

## Deployment Status
Auto-deployed from GitHub via Vercel

## Features

- 🚀 Simple chat interface for data collection
- 📊 Automatic blower sizing calculations
- 🔧 Product recommendations based on requirements
- 💾 Quote generation and storage
- 🌐 Embeddable widget for any website
- 📱 Mobile responsive design

## Project Structure

```
blower-chatbot/
├── backend/           # FastAPI backend
│   ├── app.py        # Main API application
│   ├── calculator.py # Calculation engine
│   └── requirements.txt
├── frontend/          # Web interface
│   ├── index.html    # Standalone chat page
│   ├── widget.html   # Embeddable widget
│   ├── chat.js       # Chat logic
│   └── styles.css    # Styling
└── deploy/           # Deployment files
    ├── widget-embed.js    # Widget loader script
    └── embed-snippet.html # Installation instructions
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend will run on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend
# Serve with any static server, e.g.:
python -m http.server 8080
```

Frontend will be available at http://localhost:8080

## How It Works

### Simple Calculation Flow

1. User provides tank dimensions (L x W x H)
2. User provides altitude/location
3. System calculates:
   - Tank volume
   - Required airflow (m³/hr)
   - Required pressure (mbar)
   - Power estimate (kW)
4. System recommends matching blowers
5. Quote is generated and stored

### Current Formula (MVP)

```python
# Airflow calculation
airflow = tank_volume * air_changes_per_hour * safety_factor

# Pressure calculation
pressure = water_depth * 98.1 + system_losses + altitude_correction
```

## Embedding the Widget

### Option 1: Floating Widget (Recommended)

Add this script to your website:

```html
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'https://your-domain.com/widget-embed.js';
    script.async = true;
    document.body.appendChild(script);
})();
</script>
```

### Option 2: Iframe Embed

```html
<iframe
    src="https://your-domain.com/widget.html"
    width="400"
    height="600"
    style="border: none;">
</iframe>
```

## Deployment (Free Options)

### Backend (Render.com)

1. Create account at render.com
2. Create new Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Frontend (Netlify)

1. Create account at netlify.com
2. Drag and drop frontend folder
3. Update API URL in chat.js
4. Custom domain (optional)

## API Endpoints

- `POST /api/chat` - Handle chat conversation
- `POST /api/calculate` - Direct calculation
- `GET /api/quote/{quote_id}` - Retrieve quote

## Future Enhancements

### Phase 1 (Current - MVP)
✅ Simple tank calculations
✅ Basic chat interface
✅ Product matching
✅ Embeddable widget

### Phase 2 (Next)
- [ ] Multiple blower configurations
- [ ] Pipe loss calculations
- [ ] Different tank geometries
- [ ] PDF quote generation
- [ ] Email integration

### Phase 3 (Advanced)
- [ ] GPT integration for natural conversation
- [ ] Auto-location detection
- [ ] Historical data analysis
- [ ] Advanced product matching
- [ ] Customer portal

## Configuration

Update these in the code before deployment:

1. **Backend (app.py)**
   - CORS origins for your domain
   - Database path

2. **Frontend (chat.js)**
   - API URL to your backend
   - Session management settings

3. **Widget (widget-embed.js)**
   - WIDGET_URL to your frontend domain

## Testing

### Local Testing
1. Run backend: `python app.py`
2. Open frontend: `frontend/index.html`
3. Test conversation flow

### Widget Testing
1. Create test HTML file
2. Include embed script
3. Test on local server

## Support

For questions or issues, contact:
- Technical: developer@crelec.co.za
- Sales: sales@crelec.co.za

## License

Proprietary - Crelec S.A. 2024