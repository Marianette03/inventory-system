# Quick Start: Real-Time Analytics & Reporting

## 🚀 Getting Started in 5 Minutes

### 1. Access the Analytics Dashboard
```
1. Login to your inventory system
2. Click "Analytics" in the left sidebar
3. Your real-time dashboard loads automatically
```

### 2. View Key Performance Indicators (KPIs)
The top section shows 6 critical metrics:

| Metric | What It Shows |
|--------|--------------|
| **Total Inventory Value** | Current worth of all stock |
| **Total Products** | Number of active products |
| **Low Stock Items** | Products approaching minimum levels |
| **Out of Stock** | Products with zero quantity |
| **Turnover Ratio** | How fast inventory moves |
| **Stock Accuracy** | Quality of inventory records |

### 3. Understand the Charts

#### Category Distribution (Doughnut Chart)
- Shows inventory value split by category
- **Larger slice = More valuable category**
- Hover to see exact values

#### Profit Analysis (Bar Chart)
- **Red bars** = Cost to purchase
- **Blue bars** = Revenue from sales
- **Green bars** = Profit earned

#### Stock Trends (Line Chart)
- **Green line** = Stock coming in (purchases)
- **Red line** = Stock going out (sales)
- **Change timeframe** using buttons (7/14/30/90 days)

### 4. Monitor Alerts
Red alert boxes show issues needing attention:

```
🔴 CRITICAL (Red) = Act immediately
   Example: "Product X is out of stock"

🟠 WARNING (Orange) = Address within a day
   Example: "Product Y stock is running low"

🔵 INFO (Blue) = For your awareness
   Example: "Unusual activity detected on Product Z"
```

### 5. View Top Products
The "Top Products by Value" section shows:
- Products generating most revenue
- Quick toggle to view by quantity instead
- Perfect for identifying bestsellers

---

## 📊 Advanced Features

### Generate Demand Forecast
To predict future demand for a product:

```
1. Go to any product details page
2. Look for "Demand Forecast" section
3. System shows 30-day prediction
4. View confidence level (%) - higher is better
5. See if trend is increasing/decreasing
```

**Example Output:**
```
Forecast for "Wireless Mouse":
- Avg Daily Demand: 5.2 units
- Confidence: 78%
- Trend: Stable
- Recommended Reorder: When stock < 45 units
```

### Check Reorder Points
Automatic calculation of when to reorder:

```
API Call: /api/predictions/reorder-point/<product_id>

Returns:
- Reorder Point (ROP): Optimal quantity to trigger reorder
- Economic Order Quantity (EOQ): Ideal order size
- Current Status: REORDER or SUFFICIENT
- Recommendation: Action needed
```

### Export Analytics Report
Download full analytics as JSON:

```
1. Click "Export Report" button (top right)
2. File downloads: analytics-report-YYYY-MM-DD.json
3. Open in Excel or data analysis tool
4. Contains all metrics, trends, and predictions
```

---

## 🎯 Common Use Cases

### Use Case 1: Identify Stock Issues
```
GOAL: Find products needing immediate attention

STEPS:
1. Look at "Critical Alerts" section (top of page)
2. Check "Low Stock Items" KPI card
3. Review products in alert list
4. Click on product to view details
5. Proceed with reorder

RESULT: Prevents stockouts and lost sales
```

### Use Case 2: Analyze Best Sellers
```
GOAL: See which products are most popular

STEPS:
1. Scroll to "Top Products by Quantity"
2. See products with highest movement
3. Check profit margins
4. Compare across time periods

RESULT: Stock planning and marketing focus
```

### Use Case 3: Forecast Budget Requirements
```
GOAL: Estimate inventory purchasing needs

STEPS:
1. Open each product's demand forecast
2. Sum predicted demand across key items
3. Multiply by average cost
4. Add 20% safety buffer
5. Present to management

RESULT: Accurate budget planning
```

### Use Case 4: Monitor Profitability
```
GOAL: Track profit margins by product/category

STEPS:
1. Review "Profit Analysis" chart
2. Look at "Top Products" profit column
3. Compare cost vs selling price
4. Identify low-margin items
5. Adjust pricing or reduce order volume

RESULT: Improved margins and ROI
```

### Use Case 5: Prevent Product Waste
```
GOAL: Avoid loss from expiring inventory

STEPS:
1. Check expiry alerts (Critical section)
2. View value at risk
3. Prioritize sales/promotions
4. Track days until expiry
5. Dispose properly if expired

RESULT: Reduced waste, maintained profitability
```

---

## 📱 Mobile Tips

### Using on Smartphone
- **Landscape mode** recommended for charts
- Swipe left/right to scroll
- Tap alerts for details
- Use refresh button (bottom right) to update

### Responsive Tables
- Scroll horizontally on small screens
- All data accessible on mobile
- Touch-friendly buttons

---

## 🔄 Data Refresh & Updates

### Auto-Refresh
- Dashboard auto-refreshes every 5 minutes
- Manual refresh: Click ↻ button (bottom right)
- Last updated time shown at bottom

### Real-Time Data Sources
- Connected directly to database
- Demo mode uses sample data
- Always shows current information

---

## 💡 Pro Tips

### Tip 1: Set Up Alerts
- Configure minimum stock levels in each product
- System automatically alerts when threshold hit
- Check alerts first thing in morning

### Tip 2: Export Weekly/Monthly
- Schedule regular exports
- Build historical report
- Track trends over time
- Share with management

### Tip 3: Analyze Seasonal Patterns
- Use 90-day view for patterns
- Identify high/low seasons
- Plan ordering accordingly
- Prevent overstocking

### Tip 4: Monitor Supplier Performance
- View supplier section
- Track total value per supplier
- Monitor shipment frequency
- Switch suppliers if needed

### Tip 5: Compare Categories
- Which category is most valuable?
- Which has highest turnover?
- Which needs attention?
- Allocate resources accordingly

---

## ⚠️ Common Issues & Solutions

### Issue: "No data available"
**Solution:**
- Ensure at least 7 days of stock movements exist
- Add some products to inventory
- Make stock adjustments to generate data

### Issue: Chart not loading
**Solution:**
- Refresh page (Ctrl+R or Cmd+R)
- Check browser console (F12)
- Clear browser cache

### Issue: Forecast shows 0% confidence
**Solution:**
- Product is too new (needs 2+ weeks history)
- Very irregular sales pattern
- Check more established products first

### Issue: Alerts not updating
**Solution:**
- Click refresh button manually
- Check product minimum stock levels
- Verify alert settings

---

## 📞 Support Reference

### Quick Access Links
- Analytics Dashboard: `/analytics`
- API Docs: Check ANALYTICS_GUIDE.md
- Database Schema: `db/schema.sql`
- Configuration: Environment variables

### Files & Locations
```
backend/
├── analytics.py          # Core analytics engine
├── predictions.py        # Forecasting engine
├── alerts.py            # Alert system
└── app.py               # API endpoints (search for /api/analytics/)

frontend/templates/
└── analytics.html       # Dashboard UI
```

### Debug Commands (Python)
```python
from analytics import InventoryAnalytics

# Test connection
analytics = InventoryAnalytics(db_connection=db)
kpis = analytics.get_kpis()

# See what data is available
print(kpis)
print(analytics.get_trends(30))
print(analytics.get_critical_alerts())
```

---

## 📚 Learn More

1. **Full Documentation**: See `ANALYTICS_GUIDE.md`
2. **API Reference**: Check endpoint list in guide
3. **Database Schema**: See `db/schema.sql`
4. **Source Code**: Review `.py` files with detailed comments

---

## 🎓 Practice Exercises

### Exercise 1: Basic Metric Reading
1. Open Analytics dashboard
2. Take note of all 6 KPI values
3. Predict: What will happen next week?

### Exercise 2: Alert Management
1. Find all critical alerts
2. Read recommended actions
3. For 3 alerts, plan how to resolve

### Exercise 3: Export & Analyze
1. Export analytics report
2. Open in Excel/JSON viewer
3. Calculate totals and percentages

### Exercise 4: Forecast Interpretation
1. Select a product
2. Check 30-day demand forecast
3. Based on forecast, calculate reorder quantity

### Exercise 5: Trend Analysis
1. View 90-day stock trends
2. Identify peak activity periods
3. Predict next peak period

---

**Ready to get started?** 👉 Click "Analytics" in your sidebar now!

---

**Version:** 2.0.0 | Last Updated: April 2026
