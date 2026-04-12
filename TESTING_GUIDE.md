# QUICK TESTING GUIDE

## Pre-Test Checklist
- [ ] Python 3.6+ installed
- [ ] Flask installed (`pip install flask`)
- [ ] MySQL or XAMPP running (for database mode)
- [ ] Navigate to project folder
- [ ] Set DEMO_MODE environment variable (optional)

## Running the Application

**Demo Mode (Recommended for Testing):**
```bash
set DEMO_MODE=true
python backend/app.py
```

**Database Mode:**
```bash
python setup.py
python backend/app.py
```

Then open browser: http://localhost:5000

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

---

## Test Cases

### TEST 1: Suppliers Page - View / Edit / Delete

**Objective**: Verify supplier management modals work correctly

1. Navigate to: **Suppliers** (from sidebar)
2. Click **View** button on any supplier
   - Expected: Modal opens showing supplier details (Name, Contact, Email, Phone, Address)
   - Verify: All fields display correctly
   - Action: Click "Close" button → Modal closes

3. Click **Edit** button on same supplier
   - Expected: Modal opens with edit form pre-filled with current data
   - Verify: All fields show current values
   - Action: 
     - Change Name to "Test Supplier"
     - Click "Update Supplier" button
     - Expected: Modal closes, update appears successful
     - Check: Supplier list shows updated name

4. Click **Delete** button on another supplier
   - Expected: Confirmation modal appears with supplier name
   - Verify: Name is displayed correctly (check for special characters)
   - Action:
     - Click "Cancel" → Modal closes (no deletion)
     - Click "Delete" again and confirm → Supplier removed from list

**PASS**: All modals open/close correctly and data persists ✓

---

### TEST 2: Add New Product

**Objective**: Verify product creation with simplified form

1. Navigate to: **Inventory** → Click "Add Product"
2. Observe form layout
   - Expected: Simple form with 3 sections (Basic Info, Inventory, Pricing)
   - Verify: No extra fields like description, location, batch number

3. Fill form:
   - Product Name: "Test Product"
   - Category: Select "Electronics"
   - Unit: Select "Pieces"
   - Leave SKU empty (should auto-generate)
   - Leave Barcode empty (should auto-generate)
   - Quantity: 100
   - Min Stock Level: 20
   - Cost Price: 500

4. Verify auto-calculations:
   - Tab out of Cost Price field
   - Expected: Selling Price field auto-fills with 650 (500 × 1.3)

5. Click "Save Product"
   - Expected: Redirect to Inventory page
   - Verify: New product appears in list
   - Check: SKU is auto-generated (not empty)
   - Check: Barcode is auto-generated (not empty)

**PASS**: Form simplified, auto-generation works, product created ✓

---

### TEST 3: Delete Product from Inventory

**Objective**: Verify delete functionality with proper XSS protection

1. On **Inventory** page, find any product
2. Click **Delete** icon (trash can) for that product
3. Observe confirmation modal
   - Expected: Modal shows "Are you sure you want to delete '[Product Name]'?"
   - Verify: Product name displays correctly
   - Test Special Characters: Try deleting a product with apostrophe or quotes in name
     - Expected: Modal still shows correctly (no JavaScript error)

4. Click "Delete Product" to confirm
   - Expected: Modal closes
   - Verify: Product removed from inventory list
   - Check: No errors in browser console

**PASS**: Delete works correctly with proper escaping ✓

---

### TEST 4: Dashboard Alerts - Dismiss Alerts

**Objective**: Verify alert dismissal functionality

1. Navigate to: **Dashboard**
2. Scroll to "System Alerts" section
3. Observe alerts
   - Expected: One or more "Low stock" alerts shown
   - Verify: Each alert has X button on the right

4. Click **X button** on any alert
   - Expected: Alert smoothly disappears
   - Verify: Success message briefly shows ("Alert dismissed.")
   - Check: "Active Alerts" count in stat box decreases by 1

5. Refresh page (F5)
   - Expected: Alert should remain gone (dismissed state persists)

6. Create new product with low stock level
   - Go to Inventory → Add Product
   - Set Minimum Stock Level to 50, Initial Quantity to 10
   - Save product
   - Return to Dashboard
   - Expected: New low stock alert appears in System Alerts

**PASS**: Alerts display, dismiss correctly, count updates ✓

---

### TEST 5: Modal Interactions

**Objective**: Verify all modal open/close mechanisms

1. On any page with modals (Suppliers, Inventory)
2. Open a modal (by clicking View/Edit/Delete button)
3. Test Close Methods:
   - **X Button**: Click × in top-right → Modal closes
   - **Cancel Button**: Click "Cancel" → Modal closes  
   - **Escape Key**: Press Esc → Modal closes
   - **Click Outside**: Click outside modal box → Modal closes

4. Modal Should NOT Close:
   - When filling form fields
   - When clicking inside modal content area

**PASS**: All modal interactions work correctly ✓

---

### TEST 6: Form Field Validation

**Objective**: Verify form validation and error handling

1. On "Add Product" page:
   - Try submitting with empty required fields
   - Expected: Browser validation shows "Please fill in this field" message

2. Try entering selling price less than cost price
   - Cost Price: 100
   - Selling Price: 50
   - Click Save
   - Expected: JavaScript alert shows "Selling price should be higher than cost price"

3. Fill all fields correctly and submit
   - Expected: Product added successfully

**PASS**: Validation works as expected ✓

---

### TEST 7: Supplier Edit Operations

**Objective**: Verify supplier data persists after edits

1. Go to **Suppliers** page
2. Note supplier details (Name, Email, Phone)
3. Click Edit on that supplier
4. Change Contact Person field to "New Contact"
5. Click "Update Supplier"
6. Click View on same supplier
   - Expected: Contact Person now shows "New Contact"
7. Edit again, change Email to "newemail@example.com"
8. Click "Update Supplier"
9. Click View again
   - Expected: Email shows "newemail@example.com"

**PASS**: Edits persist correctly ✓

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Modals don't open | Check browser console for JS errors. Verify modal IDs exist in HTML. |
| Delete doesn't work | Verify backend route exists. Check Flask logs for errors. |
| Alert count doesn't decrease | Verify main.js loadedInclude all needed. Try browser console clear. |
| Form won't submit | Check required fields are filled. Verify Backend route handler exists. |
| Products don't save | Check DEMO_MODE setting. Verify database connection if not DEMO_MODE. |

---

## Success Indicators

✓ All pages load without errors
✓ Modals open/close smoothly
✓ Forms submit and save data
✓ Alerts can be dismissed
✓ Delete operations work
✓ Edit operations persist
✓ No JavaScript errors in console
✓ No SQL errors in terminal
✓ Page redirects work correctly

---

**Last Updated**: April 12, 2026
**Estimated Test Time**: 15-20 minutes
