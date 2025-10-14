# Dynamic Google Sheets Integration - Auto-Adapting Columns

This solution automatically handles any column changes without needing to update code!

## The Problem
- Google Sheets API requires authentication (OAuth or Service Account)
- Direct API calls aren't possible without credentials
- Columns change frequently, so hardcoding is bad

## The Solution: Smart Google Apps Script

Instead of hardcoding columns, we'll create a **dynamic webhook** that automatically adapts to ANY data structure you send!

## One-Time Setup (3 minutes)

### Step 1: Create Your Google Sheet

1. Go to Google Sheets (logged in as brphobost@gmail.com)
2. Create a new sheet: "Crelec Inquiries Dynamic"
3. **Leave Row 1 empty** - The script will create headers automatically!

### Step 2: Add the Smart Script

1. In your sheet, go to **Extensions → Apps Script**
2. Delete everything and paste this smart code:

```javascript
// DYNAMIC GOOGLE SHEETS WEBHOOK
// Automatically handles any data structure!

function doPost(e) {
  try {
    // Parse incoming data
    var data = JSON.parse(e.postData.contents);

    // Get the active sheet
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Add timestamp if not present
    if (!data.timestamp) {
      data.timestamp = new Date().toLocaleString('en-US', {
        timeZone: 'Africa/Johannesburg'
      });
    }

    // Get existing headers from Row 1
    var lastColumn = sheet.getLastColumn();
    var headers = [];

    if (lastColumn > 0) {
      headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];
    }

    // Get all keys from the incoming data
    var dataKeys = Object.keys(data);

    // Add any new columns that don't exist
    var columnsAdded = false;
    dataKeys.forEach(function(key) {
      if (headers.indexOf(key) === -1) {
        headers.push(key);
        columnsAdded = true;
      }
    });

    // Update headers if new columns were added
    if (columnsAdded || headers.length === 0) {
      // Clear and rewrite all headers
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

      // Make headers bold and colored
      sheet.getRange(1, 1, 1, headers.length)
        .setFontWeight('bold')
        .setBackground('#0066cc')
        .setFontColor('#ffffff');
    }

    // Create row data in the correct order
    var rowData = [];
    headers.forEach(function(header) {
      var value = data[header];

      // Handle different data types
      if (value === undefined || value === null) {
        rowData.push('');
      } else if (typeof value === 'object') {
        rowData.push(JSON.stringify(value));
      } else {
        rowData.push(value);
      }
    });

    // Append the row
    sheet.appendRow(rowData);

    // Auto-resize columns for better readability
    if (sheet.getLastRow() <= 2) {
      sheet.autoResizeColumns(1, headers.length);
    }

    // Log success
    console.log('Data logged successfully:', JSON.stringify(data));

    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({
        status: 'success',
        message: 'Data logged',
        columns: headers.length,
        row: sheet.getLastRow()
      }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch(error) {
    console.error('Error:', error.toString());

    return ContentService
      .createTextOutput(JSON.stringify({
        status: 'error',
        message: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// GET endpoint for testing
function doGet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var lastColumn = sheet.getLastColumn();

  var headers = [];
  if (lastColumn > 0 && lastRow > 0) {
    headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];
  }

  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ready',
      message: 'Dynamic webhook is active',
      sheet: SpreadsheetApp.getActiveSpreadsheet().getName(),
      rows: lastRow,
      columns: headers.length,
      headers: headers,
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Utility function to get all data (optional)
function getAllData() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  return data;
}
```

3. Save it (Ctrl+S) and name it "Dynamic Webhook"

### Step 3: Deploy the Webhook

1. Click **Deploy → New Deployment**
2. Click settings ⚙️ → **Web app**
3. Settings:
   - **Description**: Dynamic Crelec Logger
   - **Execute as**: Me
   - **Who has access**: Anyone
4. Click **Deploy**
5. **Copy the URL** (like: `https://script.google.com/macros/s/AKfycbw.../exec`)

### Step 4: Update Your Chatbot

Just update `api/config.py`:
```python
GOOGLE_SHEETS_WEBHOOK = "YOUR_URL_HERE"
```

## How It Works

### Automatic Column Management
- **First data sent**: Creates headers automatically
- **New field added**: Automatically adds new column
- **Field removed**: Column stays but gets empty values
- **Field renamed**: Creates new column (old one remains)

### Example Flow

**Day 1**: You send this data:
```json
{
  "email": "test@example.com",
  "application": "waste_water",
  "pressure": 500
}
```
Sheet creates: `email | application | pressure`

**Day 2**: You add new fields:
```json
{
  "email": "test2@example.com",
  "application": "fish_farm",
  "pressure": 600,
  "temperature": 25,
  "new_field": "test"
}
```
Sheet automatically adds: `email | application | pressure | temperature | new_field`

**Day 3**: Fields change again:
```json
{
  "email": "test3@example.com",
  "application": "industrial",
  "airflow": 300,
  "totally_different": "value"
}
```
Sheet adds: `email | application | pressure | temperature | new_field | airflow | totally_different`

Old columns remain, new ones are added automatically!

## Benefits

✅ **Zero Maintenance** - Never update the script again
✅ **Fully Dynamic** - Handles any data structure
✅ **Backwards Compatible** - Old columns preserved
✅ **Auto-Formatting** - Headers styled automatically
✅ **No Authentication in Chatbot** - Just POST to webhook
✅ **Free Forever** - Google's free tier

## Testing Your Webhook

1. Visit your webhook URL in browser
2. You should see:
```json
{
  "status": "ready",
  "message": "Dynamic webhook is active",
  "headers": ["timestamp", "email", ...],
  "rows": 0
}
```

## Advanced Features

### View Specific Data Range
Add to your Apps Script:
```javascript
function getRecentEntries(n = 10) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return [];

  var startRow = Math.max(2, lastRow - n + 1);
  var numRows = lastRow - startRow + 1;
  var data = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn()).getValues();
  return data;
}
```

### Email Notifications (Optional)
Add after `sheet.appendRow(rowData);`:
```javascript
// Send email for new inquiries
if (data.email) {
  MailApp.sendEmail({
    to: 'brphobost@gmail.com',
    subject: 'New Inquiry: ' + data.email,
    body: 'New inquiry received\n\n' + JSON.stringify(data, null, 2)
  });
}
```

## That's It!

Once you set this up, you never need to touch it again. The webhook automatically adapts to ANY data structure changes!