# Google Sheets Setup for brphobost@gmail.com

Follow these steps to set up your Google Sheets data logging:

## Step 1: Create the Google Sheet

1. Click this link while logged in as **brphobost@gmail.com**:
   https://sheets.new

2. Name the spreadsheet: **"Crelec Blower Inquiries Log"**

3. Copy and paste this header row into Row 1:
   ```
   Timestamp	Quote ID	Email	Application	Environment	Operation	Altitude	Location	Tanks	Config	Length	Width	Depth	Pipe Dia	Pipe Len	Bends	Diffuser	Airflow	Pressure	Power
   ```

   Or manually create these column headers in Row 1:
   - A1: Timestamp
   - B1: Quote ID
   - C1: Email
   - D1: Application
   - E1: Environment
   - F1: Operation
   - G1: Altitude
   - H1: Location
   - I1: Tanks
   - J1: Config
   - K1: Length
   - L1: Width
   - M1: Depth
   - N1: Pipe Dia
   - O1: Pipe Len
   - P1: Bends
   - Q1: Diffuser
   - R1: Airflow
   - S1: Pressure
   - T1: Power

## Step 2: Create the Apps Script

1. In your Google Sheet, go to **Extensions → Apps Script**

2. Delete all existing code and paste this exactly:

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

    // Log for debugging
    console.log('Data received:', JSON.stringify(data));

    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({
        status: 'success',
        message: 'Data logged successfully',
        row: sheet.getLastRow()
      }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch(error) {
    console.error('Error:', error.toString());

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
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ready',
      message: 'Crelec inquiry logger is active',
      spreadsheet: SpreadsheetApp.getActiveSpreadsheet().getName(),
      totalRows: lastRow,
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Optional: Email notification for new inquiries
function sendNotification(data) {
  // Uncomment to enable email notifications
  /*
  if (data.email) {
    MailApp.sendEmail({
      to: 'brphobost@gmail.com',
      subject: 'New Crelec Blower Inquiry: ' + data.email,
      body: 'New inquiry received\n\n' +
            'Email: ' + data.email + '\n' +
            'Application: ' + data.application + '\n' +
            'Quote ID: ' + data.quote_id + '\n\n' +
            'View in sheet: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
    });
  }
  */
}
```

3. Save the file (Ctrl+S or Cmd+S)
4. Name it: **"Crelec Inquiry Logger"**

## Step 3: Deploy the Web App

1. In Apps Script, click **Deploy → New Deployment**

2. Click the settings gear ⚙️ and select **"Web app"**

3. Fill in these exact settings:
   - **Description**: Crelec Blower Inquiry Logger v1
   - **Execute as**: Me (brphobost@gmail.com)
   - **Who has access**: Anyone

4. Click **Deploy**

5. You'll see a screen with your Web App URL. It will look like:
   ```
   https://script.google.com/macros/s/AKfycbw.../exec
   ```

6. **COPY THIS URL** - This is your webhook URL!

7. Click **Done**

## Step 4: Test Your Webhook

1. Open a new browser tab
2. Paste your webhook URL and press Enter
3. You should see something like:
   ```json
   {
     "status": "ready",
     "message": "Crelec inquiry logger is active",
     "spreadsheet": "Crelec Blower Inquiries Log",
     "totalRows": 1,
     "timestamp": "2024-10-14T..."
   }
   ```

## Step 5: Update Your Chatbot Configuration

1. In your project folder, go to `/api/`

2. Copy `config.example.py` to `config.py`:
   ```bash
   cp api/config.example.py api/config.py
   ```

3. Edit `api/config.py` and paste your webhook URL:
   ```python
   GOOGLE_SHEETS_WEBHOOK = "YOUR_WEBHOOK_URL_HERE"
   ```

   Example:
   ```python
   GOOGLE_SHEETS_WEBHOOK = "https://script.google.com/macros/s/AKfycbwabcdef.../exec"
   ```

4. Save the file

## Step 6: Deploy and Test

Since you're using Vercel:

1. Commit and push your config:
   ```bash
   git add api/config.py
   git commit -m "Add Google Sheets webhook URL"
   git push origin master
   ```

2. Wait 1-2 minutes for Vercel to deploy

3. Test the chatbot and complete a full inquiry

4. Check your Google Sheet - you should see the data appear!

## Troubleshooting

**If data doesn't appear:**
1. Check the webhook URL is correct (no spaces, complete URL)
2. In Apps Script, go to **View → Executions** to see any errors
3. Make sure the sheet has headers in Row 1
4. Try re-deploying: Deploy → Manage Deployments → Edit → New Version

**To see logs:**
1. In Apps Script, click **View → Executions**
2. You can see each webhook call and any errors

## Optional Features

### Enable Email Notifications
1. In the Apps Script, uncomment the email notification section
2. Change the email address to where you want notifications
3. Deploy a new version

### Add Data Validation
1. In your Google Sheet, select column C (Email)
2. Data → Data validation → Add rule
3. Criteria: Text contains @
4. This ensures email format is correct

### Create Charts
1. Select your data range
2. Insert → Chart
3. Suggested charts:
   - Pie chart of Applications
   - Timeline of inquiries per day
   - Bar chart of environment types

## Your Webhook URL

Once you complete Step 3, paste your webhook URL here:

```
YOUR_WEBHOOK_URL = [Paste here after deployment]
```

Then I can help you update the config.py file!

---

**Need help?** Let me know at which step you need assistance!