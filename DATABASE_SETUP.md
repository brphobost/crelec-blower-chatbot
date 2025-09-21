# Quote Database Setup

## Overview
Every generated quote is now automatically logged with:
- Customer email
- Tank dimensions and calculations
- Recommended products
- Timestamp and session ID

## Current Implementation (v1.2.0)

### 1. Automatic Logging
All quotes are automatically:
- Logged to Vercel console (visible in Vercel dashboard)
- Saved to `/tmp/quotes.json` (temporary, resets on deployment)
- Ready to send to Google Sheets (needs setup)

### 2. Data Captured
```json
{
  "quote_id": "Q20250921-ABC123",
  "timestamp": "2025-09-21T10:30:00",
  "customer": {
    "email": "customer@example.com",
    "application": "Waste Water Treatment",
    "tank_dimensions": {
      "length": 6,
      "width": 3,
      "height": 2
    },
    "altitude": 500
  },
  "calculation": {
    "tank_volume": 36,
    "airflow_required": 43.2,
    "pressure_required": 320.1,
    "power_estimate": 0.01
  },
  "recommended_products": [
    {
      "model": "RB-550",
      "price": 12500,
      "match_score": 100
    }
  ],
  "session_id": "abc123",
  "ip_address": "196.25.xxx.xxx",
  "user_agent": "Mozilla/5.0..."
}
```

## Google Sheets Integration (Recommended)

### Benefits:
- Free and easy to access
- Real-time updates
- Easy to share with Crelec team
- Can create charts/reports

### Setup Instructions:

#### Step 1: Create Google Sheet
1. Create new Google Sheet
2. Name it "Crelec Quote Tracker"
3. Add these column headers in row 1:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Quote ID | Email | Application | Tank Length | Tank Width | Tank Height | Tank Volume | Altitude | Airflow Required | Pressure Required | Power Estimate | Products Count | Product 1 | Product 1 Price | Session ID |

#### Step 2: Create Apps Script
1. In your Google Sheet, go to **Extensions > Apps Script**
2. Delete any existing code
3. Paste this code:

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    data.timestamp,
    data.quote_id,
    data.email,
    data.application,
    data.tank_length,
    data.tank_width,
    data.tank_height,
    data.tank_volume,
    data.altitude,
    data.airflow_required,
    data.pressure_required,
    data.power_estimate,
    data.products_recommended,
    data.product_1,
    data.product_1_price,
    data.session_id
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({status: 'success'}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

4. Save the project (name it "Quote Logger")

#### Step 3: Deploy Web App
1. Click **Deploy > New Deployment**
2. Settings:
   - Type: **Web app**
   - Description: "Quote Logger"
   - Execute as: **Me**
   - Who has access: **Anyone**
3. Click **Deploy**
4. Copy the Web App URL (looks like: `https://script.google.com/macros/s/AKfycb.../exec`)

#### Step 4: Add to Vercel
1. Go to Vercel Dashboard
2. Select your project
3. Settings > Environment Variables
4. Add:
   - Name: `SHEETS_WEBHOOK_URL`
   - Value: Your Web App URL from step 3
5. Save and redeploy

## Alternative Storage Options

### 1. Vercel KV (Redis)
- Built-in to Vercel
- 30MB free tier
- Persistent storage
- Good for production

### 2. Supabase (PostgreSQL)
- Professional database
- Free tier: 500MB
- Good for scaling
- Real-time features

### 3. Airtable
- Better UI than Sheets
- API included
- Free tier: 1200 records
- Good for CRM features

### 4. MongoDB Atlas
- NoSQL database
- 512MB free tier
- Good for complex data
- Professional solution

## Viewing Quotes (Current)

### In Vercel Dashboard:
1. Go to your project in Vercel
2. Click on "Functions" tab
3. Click on "save_quote"
4. View logs to see all quotes

### In Browser Console:
When testing locally, quotes are logged to console with prefix `QUOTE_GENERATED:`

## Data Privacy Notes
- Email addresses are stored securely
- No credit card or payment data collected
- Data used only for quote tracking
- Can be deleted on request

## Future Enhancements
- [ ] Add admin dashboard to view quotes
- [ ] Email notifications for new quotes
- [ ] Export quotes to CSV
- [ ] Analytics dashboard
- [ ] Follow-up reminders
- [ ] Quote status tracking (sent/viewed/accepted)