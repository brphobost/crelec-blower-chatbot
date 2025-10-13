# Xero Inventory Integration for Crelec Blower Chatbot

## Overview
Xero is a cloud-based accounting software that Crelec uses to manage their inventory. We need to integrate with Xero's API to fetch real-time inventory data for the blower products, ensuring accurate stock levels and pricing in the chatbot.

## What is Xero?
- **Cloud-based accounting platform** for small to medium businesses
- **Real-time inventory management** with stock tracking
- **API-first architecture** enabling third-party integrations
- **Used by Crelec** for tracking blower inventory and pricing

## Integration Benefits
1. **Real-time stock levels** - No more manual updates
2. **Accurate pricing** - Always shows current prices
3. **Automatic sync** - Inventory updates reflect immediately
4. **Reduced errors** - Eliminates manual data entry mistakes
5. **Single source of truth** - Xero becomes the master inventory system

## Xero API Key Features for Our Use Case

### Items API (What We Need)
- **GET /Items** - Fetch all inventory items
- **GET /Items/{ItemID}** - Get specific item details
- Fields we can access:
  - `Code` - Product SKU/Model number
  - `Name` - Product name
  - `Description` - Product details
  - `QuantityOnHand` - Current stock level
  - `SalesDetails.UnitPrice` - Current selling price
  - `IsTrackedAsInventory` - Whether stock is tracked
  - `IsSold` - Whether item is for sale
  - `InventoryAssetAccountCode` - For tracked items

### API Limits
- **5,000 API calls** per day per organization
- **60 calls per minute** rate limit
- **5 concurrent requests** maximum
- Resets at midnight UTC

## Integration Architecture

```
Crelec Xero Account
        ↓
   Xero API (OAuth 2.0)
        ↓
  Our Backend Service
        ↓
   Product Database
        ↓
   Chatbot Frontend
```

## Implementation Plan

### Phase 1: Setup & Authentication
1. **Register App with Xero**
   - Create app at developer.xero.com
   - Get Client ID and Client Secret
   - Set redirect URI for OAuth flow

2. **Authentication Options**
   - **Option A: OAuth 2.0** (Recommended for multi-tenant)
     - User authorizes once
     - Refresh token every 30 minutes
     - More secure for production

   - **Option B: Custom Connection** (Premium feature)
     - Machine-to-machine auth
     - No user interaction needed
     - Requires Xero premium subscription

### Phase 2: Data Mapping
Map Xero inventory fields to our chatbot database:

| Xero Field | Our Database Field | Example |
|------------|-------------------|---------|
| Code | model | "GHBH-2D-720-H37" |
| Name | description | "Goorui Side Channel Blower" |
| QuantityOnHand | stock_level | 5 |
| SalesDetails.UnitPrice | price | 15000.00 |
| Description | specifications | "720m³/hr, 300mbar, 5.5kW" |

### Phase 3: Sync Implementation

```python
# Example sync function
import requests
from datetime import datetime

class XeroInventorySync:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def authenticate(self):
        # OAuth 2.0 flow
        # Get access token
        pass

    def fetch_inventory(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Xero-tenant-id': 'YOUR_TENANT_ID',
            'Accept': 'application/json'
        }

        response = requests.get(
            'https://api.xero.com/api.xro/2.0/Items',
            headers=headers,
            params={'where': 'IsTrackedAsInventory==true'}
        )

        return response.json()

    def sync_to_database(self):
        items = self.fetch_inventory()

        for item in items['Items']:
            # Extract blower specifications from description
            # Update our product database
            product = {
                'model': item['Code'],
                'name': item['Name'],
                'stock': item['QuantityOnHand'],
                'price': item['SalesDetails']['UnitPrice'],
                'in_stock': item['QuantityOnHand'] > 0
            }
            # Save to database
            update_product_catalog(product)
```

### Phase 4: Automation
1. **Scheduled Sync**
   - Run every 15 minutes during business hours
   - Daily full sync at midnight
   - Webhook for instant updates (if available)

2. **Error Handling**
   - Retry logic for API failures
   - Fallback to cached data
   - Alert on sync failures

## Required Information from Customer

To proceed with integration, we need:

1. **Xero Organization Details**
   - Organization name in Xero
   - Tenant ID (found in Xero settings)

2. **Product Identification**
   - How blowers are coded in Xero (SKU format)
   - Which fields contain specifications
   - Custom fields used (if any)

3. **Access Level**
   - Standard or Premium Xero subscription?
   - Who will authorize the OAuth connection?
   - Preferred sync frequency

4. **Technical Details**
   - Sample export of current inventory
   - List of all blower models in Xero
   - Any custom categories or tags used

## Security Considerations

1. **API Credentials**
   - Store in environment variables
   - Never commit to repository
   - Use secrets management service

2. **Data Protection**
   - Encrypt tokens at rest
   - Use HTTPS for all API calls
   - Implement proper error logging

3. **Access Control**
   - Minimum required permissions
   - Read-only access to inventory
   - No financial data access needed

## Testing Strategy

1. **Xero Demo Company**
   - Use Xero's test environment
   - Create sample blower products
   - Test all sync scenarios

2. **Integration Tests**
   - Mock API responses
   - Test error handling
   - Verify data mapping

3. **Production Testing**
   - Start with single product
   - Gradual rollout
   - Monitor API usage

## Estimated Timeline

- **Week 1**: Setup Xero app, authentication
- **Week 2**: Build sync module, data mapping
- **Week 3**: Testing with demo company
- **Week 4**: Production deployment, monitoring

## Cost Analysis

### Xero API Costs
- **API Access**: Free with Xero subscription
- **Premium Features**: Custom Connections require premium plan (~$10-20/month extra)

### Development Costs
- **Initial Integration**: 40-60 hours
- **Testing & Deployment**: 20 hours
- **Maintenance**: 2-4 hours/month

### ROI Benefits
- **Time Saved**: 5-10 hours/week on manual updates
- **Error Reduction**: 95% fewer pricing mistakes
- **Customer Satisfaction**: Real-time accurate quotes

## Alternative: Simplified Webhook Approach

If full API integration is complex, consider:

1. **Xero Webhooks** (if available)
   - Real-time notifications on inventory changes
   - Lower API call usage
   - Simpler implementation

2. **CSV Export Integration**
   - Daily automated export from Xero
   - Upload to our system
   - Simpler but less real-time

3. **Zapier/Make Integration**
   - No-code solution
   - Connect Xero to Google Sheets
   - Keep existing Google Sheets integration

## Next Steps

1. **Get Xero API access credentials** from customer
2. **Review their current inventory structure** in Xero
3. **Create test Xero developer account**
4. **Build proof-of-concept** integration
5. **Test with sample products**
6. **Deploy to production**

## Support Resources

- **Xero Developer Portal**: https://developer.xero.com
- **API Documentation**: https://developer.xero.com/documentation/api/accounting/overview
- **Items API**: https://developer.xero.com/documentation/api/accounting/items
- **Python SDK**: https://github.com/XeroAPI/xero-python
- **Support Forum**: https://community.xero.com/developer

## Conclusion

Integrating Xero will provide Crelec with automated, real-time inventory management for their blower chatbot. This eliminates manual updates, reduces errors, and ensures customers always see accurate stock levels and pricing. The integration can be completed in approximately 4 weeks with proper planning and testing.