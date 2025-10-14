# Google Sheets Data Logging Setup Guide

This guide will help you set up automatic logging of all chatbot inquiries to a Google Sheet.

## Overview
Every time a user completes an inquiry through the chatbot, all their input data will be automatically logged to a Google Sheet for easy tracking and analysis.

## Step 1: Create Your Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it: "Crelec Blower Inquiries Log"
4. In Row 1, add these column headers:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Quote ID | Email | Application | Environment | Operation | Altitude | Location | Tanks | Config | Length | Width | Depth | Pipe Dia | Pipe Len | Bends | Diffuser | Airflow | Pressure | Power |

## Step 2: Create Google Apps Script Web App

1. In your Google Sheet, go to **Extensions → Apps Script**
2. Delete any existing code and paste this:

```javascript
function doPost(e) {
  try {
    // Parse the incoming data
    var data = JSON.parse(e.postData.contents);

    // Open the active spreadsheet
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Create timestamp
    var timestamp = new Date();

    // Create the row data
    var row = [
      timestamp.toLocaleString('en-US', {timeZone: 'Africa/Johannesburg'}),
      data.quote_id || '',
      data.email || '',
      data.application || '',
      data.environment || '',
      data.operation_type || '',
      data.altitude || '',
      data.location || '',
      data.num_tanks || '',
      data.tank_config || '',
      data.length || '',
      data.width || '',
      data.height || '',
      data.pipe_diameter || '',
      data.pipe_length || '',
      data.num_bends || '',
      data.diffuser_type || '',
      data.airflow_m3_hr || '',
      data.pressure_mbar || '',
      data.power_kw || ''
    ];

    // Append the row to the sheet
    sheet.appendRow(row);

    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({
        status: 'success',
        message: 'Data logged successfully',
        row: sheet.getLastRow()
      }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch(error) {
    // Return error response
    return ContentService
      .createTextOutput(JSON.stringify({
        status: 'error',
        message: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Test endpoint
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ready',
      message: 'Crelec inquiry logger is active',
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

3. Save the script (Ctrl+S or Cmd+S)
4. Name it: "Crelec Inquiry Logger"

## Step 3: Deploy as Web App

1. Click **Deploy → New Deployment**
2. Click the gear icon ⚙️ and select **Web app**
3. Configure as follows:
   - **Description**: "Crelec Blower Inquiry Logger v1"
   - **Execute as**: Me (your email)
   - **Who has access**: Anyone
4. Click **Deploy**
5. **COPY THE WEB APP URL** - It will look like:
   ```
   https://script.google.com/macros/s/AKfycbw.../exec
   ```
6. **IMPORTANT**: Save this URL - you'll need it for the next step

## Step 4: Test the Webhook

Visit your Web App URL in a browser. You should see:
```json
{
  "status": "ready",
  "message": "Crelec inquiry logger is active",
  "timestamp": "2024-10-14T..."
}
```

## Step 5: Update the Chatbot Code

Once you have your Web App URL, share it with me and I'll add the logging functionality to send data like this:

```python
# This will be added to the chatbot when email is collected
def log_to_sheets(session_data, calculation_result):
    webhook_url = "YOUR_WEB_APP_URL_HERE"

    payload = {
        'quote_id': session_data.get('quote_id'),
        'email': session_data.get('email'),
        'application': session_data.get('application'),
        'environment': session_data.get('environment'),
        'operation_type': session_data.get('operation_type'),
        'altitude': session_data.get('altitude'),
        'location': session_data.get('location'),
        'num_tanks': session_data.get('num_tanks'),
        'tank_config': session_data.get('tank_config'),
        'length': session_data.get('length'),
        'width': session_data.get('width'),
        'height': session_data.get('height'),
        'pipe_diameter': session_data.get('pipe_diameter'),
        'pipe_length': session_data.get('pipe_length'),
        'num_bends': session_data.get('num_bends'),
        'diffuser_type': session_data.get('diffuser_type'),
        'airflow_m3_hr': calculation_result.get('airflow_m3_hr'),
        'pressure_mbar': calculation_result.get('pressure_mbar'),
        'power_kw': calculation_result.get('power_kw')
    }

    # Send to Google Sheets
    urllib.request.urlopen(webhook_url, json.dumps(payload).encode())
```

## Step 6: View Your Data

1. Open your Google Sheet
2. Data will appear in real-time as users complete inquiries
3. You can:
   - Sort and filter data
   - Create charts and reports
   - Export to Excel
   - Share with team members
   - Set up email notifications

## Features of This Setup

✅ **No Authentication Required** - Works with public webhook
✅ **Real-time Updates** - Data appears instantly
✅ **Free Forever** - Uses Google's free tier
✅ **Automatic Timestamps** - South African timezone
✅ **Complete Data Capture** - All user inputs saved
✅ **Easy Export** - Download as Excel anytime

## Optional Enhancements

### Add Email Notifications
In Apps Script, add this to get emailed for each inquiry:
```javascript
// Add after sheet.appendRow(row);
if (data.email) {
  MailApp.sendEmail({
    to: 'sales@crelec.co.za',
    subject: 'New Blower Inquiry: ' + data.email,
    body: 'View in sheet: ' + sheet.getUrl()
  });
}
```

### Create Charts Dashboard
1. In Google Sheets, go to Insert → Chart
2. Create charts for:
   - Most common applications
   - Average power requirements
   - Inquiries per day
   - Environment conditions distribution

### Set Up Filters
1. Select all data (Ctrl+A)
2. Data → Create a filter
3. Now you can quickly filter by any column

## Quotas & Limits
- **Free Tier**: 20,000 API calls per day
- **Row Limit**: 10 million cells per spreadsheet
- **Performance**: Instant for up to 100,000 rows

## Troubleshooting

**Data not appearing?**
- Check the Web App URL is correct
- Ensure the sheet has headers in row 1
- Verify the script is deployed

**Wrong timezone?**
- Change 'Africa/Johannesburg' in the script to your timezone

**Need to update the script?**
1. Make changes in Apps Script
2. Deploy → Manage Deployments
3. Click pencil icon → Version → New version
4. Update

## Security Notes
- The webhook URL is public but only accepts POST with JSON
- No sensitive data is exposed
- Google handles all security
- You control who can view the sheet

---

**Next Step**: Once you've created the Web App and have the URL, share it with me and I'll integrate it into the chatbot!