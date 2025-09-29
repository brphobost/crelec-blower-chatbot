# Google Sheets Product Catalog Integration

## Why Google Sheets?
- **Customer Control**: Non-technical staff can update products
- **Real-time Updates**: Changes reflect immediately (no deployment needed)
- **Version History**: Google tracks all changes automatically
- **Collaboration**: Multiple people can update simultaneously
- **Cost**: Free for business use
- **API Ready**: Easy migration path to ERP systems

## Quick Setup (5 minutes)

### Step 1: Create Google Sheet from Template

1. Copy this template: [Click to copy template](https://docs.google.com/spreadsheets/d/1_TEMPLATE_ID_/copy)
2. Or create new sheet with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| A: ID | Unique product code | GIS36-2RB |
| B: Model | Display model name | Griffin GIS 36 2RB |
| C: Brand | Manufacturer | Griffin |
| D: Airflow Min | Min m³/hr | 500 |
| E: Airflow Max | Max m³/hr | 800 |
| F: Pressure Min | Min mbar | 300 |
| G: Pressure Max | Max mbar | 500 |
| H: Power | kW rating | 5.5 |
| I: Price | ZAR price | 45000 |
| J: Currency | Currency code | ZAR |
| K: Stock Status | in_stock/low_stock/on_order | in_stock |
| L: Delivery Days | Lead time | 0 |
| M: Description | Product description | High efficiency blower |
| N: Warranty Years | Warranty period | 2 |
| O: Efficiency Rating | IE rating | IE3 |
| P: Noise Level | dB rating | 72 |
| Q: Last Updated | Date updated | 2024-09-28 |

### Step 2: Make Sheet Accessible

**Option A: Public Read-Only (Easiest)**
1. Click "Share" button
2. Change to "Anyone with the link"
3. Set as "Viewer"
4. Copy sheet ID from URL: `docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`

**Option B: Private with API Key (More Secure)**
1. Enable Google Sheets API in Google Cloud Console
2. Create API key with Sheets API access
3. Restrict key to your domain
4. Keep sheet private

### Step 3: Update Configuration

Edit `/api/sheets_products.py`:
```python
SHEET_ID = "your-sheet-id-here"  # From sheet URL
SHEET_NAME = "Products"  # Tab name in sheet
API_KEY = ""  # Optional for private sheets
```

### Step 4: Update Chat to Use Google Sheets

Edit `/api/chat.py` to fetch from Sheets:
```python
# Instead of loading from products.json:
import urllib.request
import json

def get_products():
    try:
        # Fetch from Google Sheets API
        response = urllib.request.urlopen('https://your-domain.com/api/sheets_products')
        data = json.loads(response.read())
        return data['products']
    except:
        # Fallback to local file
        with open('frontend/products.json', 'r') as f:
            return json.load(f)['products']

PRODUCTS = get_products()
```

## Maintenance Workflow

### For Daily Updates (Sales Team)
1. Open Google Sheet
2. Update stock status column
3. Update delivery days
4. Changes reflect immediately

### For New Products (Product Manager)
1. Add new row with all details
2. System picks up automatically
3. No code changes needed

### For Price Changes (Finance)
1. Update price column
2. Add note in Last Updated column
3. Historical pricing in version history

## Advanced Features

### Stock Level Integration
```
=IMPORTDATA("https://erp.crelec.co.za/api/stock/"&A2)
```
Use Google Sheets formulas to pull from ERP

### Automated Alerts
```
=IF(K2="low_stock", SEND_EMAIL("procurement@crelec.co.za", "Low stock: "&B2), "")
```
Set up email alerts for stock levels

### Multi-Currency Support
```
=I2*GOOGLEFINANCE("CURRENCY:ZARUSD")
```
Auto-convert prices to other currencies

## Migration Path

### Phase 1: Google Sheets (Current)
- Manual updates
- Immediate deployment
- Perfect for demo/POC

### Phase 2: Sheets + ERP Sync
- Scheduled sync from ERP
- Google Apps Script automation
- Best of both worlds

### Phase 3: Direct ERP Integration
- Real-time inventory
- Automated pricing
- Full business integration

## Example Sheet Structure

```csv
ID,Model,Brand,Airflow Min,Airflow Max,Pressure Min,Pressure Max,Power,Price,Currency,Stock Status,Delivery Days
GIS36-2RB,Griffin GIS 36 2RB,Griffin,500,800,300,500,5.5,45000,ZAR,in_stock,0
HB5515,Goorui HB5515,Goorui,600,900,350,550,7.5,52000,ZAR,low_stock,14
4RB310,Sirocco 4RB310,Sirocco,300,500,200,350,3.0,32000,ZAR,in_stock,0
```

## Benefits Over Current System

| Current (products.json) | Google Sheets |
|------------------------|---------------|
| Requires code deployment | Instant updates |
| Developer needed | Anyone can update |
| No version history | Full audit trail |
| Single user editing | Multi-user collaboration |
| Static data | Can pull from ERP |
| Manual updates only | Supports formulas/automation |

## Security Considerations

1. **Read-Only Access**: Sheet is view-only via API
2. **Backup Daily**: Use Google Apps Script
3. **Validation**: Check data types in code
4. **Rate Limiting**: Cache results for 5 minutes
5. **Fallback**: Always have local products.json

## Support & Troubleshooting

### Common Issues

**Sheet not loading:**
- Check sheet is public or API key is valid
- Verify sheet ID is correct
- Ensure column order matches

**Products not showing:**
- Check required fields (Model, Airflow Max)
- Verify number formats (no commas)
- Look for empty rows

**Updates not reflecting:**
- Clear browser cache
- Check sheet permissions
- Verify API endpoint

### Testing the Integration

1. Make a test change in sheet (e.g., change a price)
2. Open chatbot and complete a quote
3. Verify new price appears
4. Should update within 30 seconds

## Next Steps

1. Upload customer's Excel catalog to Google Sheets
2. Configure column mappings
3. Set sharing permissions
4. Update API configuration
5. Test with live data

This approach gives Crelec full control over their product catalog while maintaining a professional, scalable system that can grow with their business.