# Quick Start - Real-Time Analytics & Dashboard

## Server Setup (Already Running!)

```bash
# Server is currently running on:
http://127.0.0.1:5000

# Default credentials:
Username: admin
Password: admin123
```

## Access Points

| Feature | URL | Status |
|---------|-----|--------|
| Login | http://127.0.0.1:5000/login | ✓ Working |
| Dashboard | http://127.0.0.1:5000/dashboard | ✓ Working |
| **Analytics** | **http://127.0.0.1:5000/analytics** | **✓ Real-Time** |
| Inventory | http://127.0.0.1:5000/inventory | ✓ Working |
| Reports | http://127.0.0.1:5000/reports | ✓ Working |
| Categories | http://127.0.0.1:5000/categories | ✓ Working |
| Units | http://127.0.0.1:5000/units | ✓ Working |
| Suppliers | http://127.0.0.1:5000/suppliers | ✓ Working |

## Real-Time Analytics Features

### Auto-Refresh
- **Interval:** Every 5 minutes
- **Automatic:** No user action needed
- **Smart:** Refreshes when switching back to tab

### Manual Refresh
- **Button:** ↻ in bottom-right corner
- **Animation:** Spinning circle while loading
- **Feedback:** Toast notification when complete

### Live Updates
- ✓ KPI cards update without page reload
- ✓ Charts animate with new data
- ✓ Alerts display in real-time
- ✓ Timestamp shows last update

## API Endpoints (For Developers)

### Analytics API
```
GET /api/analytics/kpis              - Key Performance Indicators
GET /api/analytics/trends            - Stock movement trends
GET /api/analytics/categories        - Category breakdown
GET /api/analytics/suppliers         - Supplier analytics
GET /api/analytics/top-products      - Top products by metric
GET /api/analytics/profit-analysis   - Profit metrics
GET /api/analytics/alerts            - Critical alerts
GET /api/analytics/dashboard-summary - Complete data
GET /api/analytics/export-report     - Export as JSON
```

### Alert API
```
GET /api/alerts/all           - All alerts
GET /api/alerts/critical      - Critical only
GET /api/alerts/summary       - Alert counts
GET /api/alerts/check-stock   - Stock level checks
GET /api/alerts/check-expiry  - Expiry checks
```

## What's New

### Enhanced Analytics Dashboard
- **Parallel Data Loading:** Fetches all data simultaneously
- **No Page Reloads:** Updates happen in-place
- **Smart Updates:** Only changed data is refreshed
- **User Notifications:** Toast messages for feedback
- **Performance:** Optimized for speed and efficiency

### Real-Time KPI Cards
- Total Inventory Value
- Total Products
- Low Stock Items
- Out of Stock Items
- Inventory Turnover Ratio
- Stock Accuracy Percentage

### Interactive Charts
- **Category Chart:** Doughnut visualization of inventory by category
- **Profit Chart:** Bar chart comparing cost/revenue/profit
- **Trends Chart:** Line chart of stock in/out movements

### Smart Alerts
- Real-time critical alerts
- Color-coded severity (Red=Critical, Orange=Warning, Blue=Info)
- Quick action recommendations
- Auto-refreshing alert list

## Testing Checklist

- [x] Server starting without errors
- [x] All 43+ routes registered
- [x] Dashboard page loading
- [x] Analytics page loading with real-time data
- [x] KPI cards updating on refresh
- [x] Charts refreshing with new data
- [x] Alerts displaying correctly
- [x] Export functionality working
- [x] Auto-refresh working (5-minute interval)
- [x] Tab visibility change detection working
- [x] Toast notifications displaying
- [x] Manual refresh button working
- [x] All API endpoints responding (200 status)

## Common Tasks

### View Real-Time Analytics
1. Click "Analytics" in sidebar
2. View all KPIs and charts
3. Auto-updates every 5 minutes

### Manually Refresh Data
1. Click ↻ button (bottom-right)
2. Wait for spinner to stop
3. See "success" notification

### Export Analytics Report
1. Click "Export Report" button
2. JSON file downloads automatically
3. Opens in your default app

### Check Inventory Status
1. View Low Stock Items KPI
2. Check Alerts section for details
3. Take action as needed

### Monitor Trends
1. View Stock Movement chart
2. Click 7/14/30/90 Days buttons
3. Analyze inbound/outbound patterns

## Performance Tips

- ✓ Works best on modern browsers (Chrome, Firefox, Safari, Edge)
- ✓ Clear browser cache if seeing old data
- ✓ Ensure JavaScript is enabled
- ✓ Check network speed for large datasets
- ✓ Close unnecessary browser tabs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Page not loading | Ensure server is running: `python backend/app.py` |
| Analytics data not updating | Click refresh button manually |
| Charts not displaying | Hard refresh browser (Ctrl+Shift+R) |
| API errors in console | Check server logs in terminal |
| No alerts showing | This is normal if all inventory is healthy |

## Support

For issues or questions:
1. Check browser console (F12 → Console tab)
2. Check server terminal for error messages
3. Clear cache and refresh browser
4. Restart server if needed

---

**Status:** Ready to Use ✓
**Real-Time Updates:** Enabled ✓
**All Systems:** Operational ✓

Last Updated: April 13, 2026
