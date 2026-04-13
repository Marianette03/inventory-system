from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from markupsafe import Markup
import mysql.connector
import os
import json
import csv
import io
from datetime import datetime, timedelta
from functools import wraps
import random
import string
import re
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics import InventoryAnalytics
from predictions import PredictiveAnalytics
from alerts import RealtimeAlertSystem

# Demo mode setup - DEFAULT TO TRUE (works without MySQL)
DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() == 'true'

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '../frontend/templates')
static_dir = os.path.join(base_dir, '../frontend/static')

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)

app.secret_key = 'admin_core_secure_key_2024'

# Custom Jinja2 filter for JavaScript escaping
def escapejs_filter(value):
    """Escape string for use in JavaScript. Prevents XSS attacks."""
    if value is None:
        return ''
    value = str(value)
    # Escape special characters for JavaScript
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace("'", "\\'")
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\t', '\\t')
    value = value.replace('<', '\\x3c')
    value = value.replace('>', '\\x3e')
    return Markup(value)

app.jinja_env.filters['escapejs'] = escapejs_filter
demo_data = {
    'categories': [
        {'id': 1, 'name': 'Electronics', 'description': 'Electronic devices and components'},
        {'id': 2, 'name': 'Hardware', 'description': 'Computer hardware and peripherals'},
        {'id': 3, 'name': 'Software', 'description': 'Software licenses and digital products'},
        {'id': 4, 'name': 'Accessories', 'description': 'Various accessories and peripherals'},
        {'id': 5, 'name': 'Consumables', 'description': 'Consumable items and supplies'},
        {'id': 6, 'name': 'Furniture', 'description': 'Office furniture and equipment'},
        {'id': 7, 'name': 'Tools', 'description': 'Tools and maintenance equipment'},
    ],
    'units': [
        {'id': 1, 'unit_name': 'Pieces', 'abbreviation': 'pcs'},
        {'id': 2, 'unit_name': 'Kilograms', 'abbreviation': 'kg'},
        {'id': 3, 'unit_name': 'Liters', 'abbreviation': 'L'},
        {'id': 4, 'unit_name': 'Boxes', 'abbreviation': 'box'},
        {'id': 5, 'unit_name': 'Meters', 'abbreviation': 'm'},
        {'id': 6, 'unit_name': 'Packets', 'abbreviation': 'pkt'},
    ],
    'suppliers': [
        {'id': 1, 'name': 'TechCorp Supplies', 'contact_person': 'John Smith', 'email': 'john@techcorp.com', 'phone': '+63 912 345 6789', 'address': '123 Business St, Makati City'},
        {'id': 2, 'name': 'Global Electronics', 'contact_person': 'Maria Garcia', 'email': 'maria@globalelec.com', 'phone': '+63 917 987 6543', 'address': '456 Commerce Ave, BGC'},
        {'id': 3, 'name': 'Office Solutions Inc', 'contact_person': 'Robert Chen', 'email': 'robert@officesol.com', 'phone': '+63 922 111 2222', 'address': '789 Corporate Blvd, Ortigas'},
    ],
    'products': [
        {'id': 1, 'name': 'Wireless Mouse', 'description': 'Ergonomic wireless optical mouse', 'category_id': 1, 'unit_id': 1, 'supplier_id': 1, 'sku': 'MS-001', 'barcode': '123456789012', 'quantity': 45, 'min_stock_level': 10, 'max_stock_level': 100, 'cost_price': 450.00, 'selling_price': 650.00, 'location': 'Shelf A1', 'expiry_date': None, 'batch_number': 'BT-001', 'status': 'active'},
        {'id': 2, 'name': 'Mechanical Keyboard', 'description': 'RGB backlit mechanical gaming keyboard', 'category_id': 1, 'unit_id': 1, 'supplier_id': 1, 'sku': 'KB-001', 'barcode': '123456789013', 'quantity': 12, 'min_stock_level': 5, 'max_stock_level': 50, 'cost_price': 2500.00, 'selling_price': 3200.00, 'location': 'Shelf A2', 'expiry_date': None, 'batch_number': 'MK-001', 'status': 'active'},
        {'id': 3, 'name': 'USB-C Cable', 'description': '1m braided USB-C to USB-C cable', 'category_id': 1, 'unit_id': 1, 'supplier_id': 1, 'sku': 'CB-001', 'barcode': '123456789014', 'quantity': 78, 'min_stock_level': 20, 'max_stock_level': 200, 'cost_price': 150.00, 'selling_price': 250.00, 'location': 'Shelf B1', 'expiry_date': None, 'batch_number': 'UC-001', 'status': 'active'},
        {'id': 4, 'name': 'External Hard Drive', 'description': '2TB portable external HDD', 'category_id': 1, 'unit_id': 1, 'supplier_id': 2, 'sku': 'HD-001', 'barcode': '123456789015', 'quantity': 8, 'min_stock_level': 3, 'max_stock_level': 25, 'cost_price': 3500.00, 'selling_price': 4200.00, 'location': 'Shelf A3', 'expiry_date': None, 'batch_number': 'EH-001', 'status': 'active'},
        {'id': 5, 'name': 'Office Chair', 'description': 'Ergonomic office chair with lumbar support', 'category_id': 6, 'unit_id': 1, 'supplier_id': 3, 'sku': 'CH-001', 'barcode': '123456789016', 'quantity': 15, 'min_stock_level': 5, 'max_stock_level': 30, 'cost_price': 8500.00, 'selling_price': 12000.00, 'location': 'Warehouse 1', 'expiry_date': None, 'batch_number': 'OC-001', 'status': 'active'},
        {'id': 6, 'name': 'Printer Paper', 'description': 'A4 size, 500 sheets per pack', 'category_id': 5, 'unit_id': 6, 'supplier_id': 3, 'sku': 'PP-001', 'barcode': '123456789017', 'quantity': 25, 'min_stock_level': 10, 'max_stock_level': 100, 'cost_price': 180.00, 'selling_price': 250.00, 'location': 'Storage Room', 'expiry_date': None, 'batch_number': 'PP-001', 'status': 'active'},
        {'id': 7, 'name': 'Network Cable', 'description': 'Cat6 Ethernet cable, 10m', 'category_id': 1, 'unit_id': 5, 'supplier_id': 1, 'sku': 'NC-001', 'barcode': '123456789018', 'quantity': 32, 'min_stock_level': 15, 'max_stock_level': 80, 'cost_price': 320.00, 'selling_price': 450.00, 'location': 'Shelf C1', 'expiry_date': None, 'batch_number': 'C6-001', 'status': 'active'},
        {'id': 8, 'name': 'Webcam', 'description': '1080p HD webcam with microphone', 'category_id': 1, 'unit_id': 1, 'supplier_id': 2, 'sku': 'WC-001', 'barcode': '123456789019', 'quantity': 6, 'min_stock_level': 3, 'max_stock_level': 20, 'cost_price': 1200.00, 'selling_price': 1800.00, 'location': 'Shelf A4', 'expiry_date': None, 'batch_number': 'WC-001', 'status': 'active'},
    ],
    'stock_movements': [],
    'alerts': [
        {'id': 1, 'product_id': 2, 'alert_type': 'low_stock', 'message': 'Low stock alert: Mechanical Keyboard has 12 remaining (min: 5)', 'is_read': False, 'created_at': datetime.now() - timedelta(hours=1)},
        {'id': 2, 'product_id': 4, 'alert_type': 'low_stock', 'message': 'Low stock alert: External Hard Drive has 8 remaining (min: 3)', 'is_read': False, 'created_at': datetime.now() - timedelta(hours=3)},
        {'id': 3, 'product_id': 8, 'alert_type': 'low_stock', 'message': 'Low stock alert: Webcam has 6 remaining (min: 3)', 'is_read': False, 'created_at': datetime.now() - timedelta(hours=5)},
    ]
}

# Demo mode helper functions
def demo_get_products():
    """Get all products for demo mode"""
    return [p for p in demo_data['products'] if p.get('status', 'active') == 'active']

def demo_get_product(product_id):
    """Get a specific product for demo mode"""
    return next((p for p in demo_data['products'] if p['id'] == product_id), None)

def demo_add_product(product):
    """Add a product in demo mode"""
    product['id'] = max(p['id'] for p in demo_data['products']) + 1 if demo_data['products'] else 1
    demo_data['products'].append(product)
    return product

def demo_update_product(product_id, product):
    """Update a product in demo mode"""
    for i, p in enumerate(demo_data['products']):
        if p['id'] == product_id:
            demo_data['products'][i].update(product)
            return demo_data['products'][i]
    return None

def demo_delete_product(product_id):
    """Delete a product in demo mode"""
    demo_data['products'] = [p for p in demo_data['products'] if p['id'] != product_id]

def demo_get_categories():
    """Get all categories for demo mode"""
    return demo_data['categories']

def demo_get_units():
    """Get all units for demo mode"""
    return demo_data['units']

def demo_get_suppliers():
    """Get all suppliers for demo mode"""
    return demo_data['suppliers']

def get_db():
    if DEMO_MODE:
        return None  # Demo mode doesn't use real database
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="inventory_db"
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_sku():
    """Generate a unique SKU"""
    return 'SKU-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_barcode():
    """Generate a unique barcode"""
    return ''.join(random.choices(string.digits, k=12))


def parse_int_or_none(value):
    """Parse an integer or return None if the value is empty or invalid."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def check_low_stock():
    """Check for low stock items and create alerts"""
    if DEMO_MODE:
        # Demo mode: check products and create alerts
        for product in demo_data['products']:
            if product['quantity'] <= product['min_stock_level']:
                alert_exists = any(a.get('product_id') == product['id'] and a.get('alert_type') == 'low_stock' and not a.get('is_read', False)
                                 for a in demo_data['alerts'])
                if not alert_exists:
                    demo_data['alerts'].append({
                        'id': len(demo_data['alerts']) + 1,
                        'product_id': product['id'],
                        'alert_type': 'low_stock',
                        'message': f"Low stock alert: {product['name']} has {product['quantity']} remaining (min: {product['min_stock_level']})",
                        'is_read': False,
                        'created_at': datetime.now()
                    })
        return

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, c.name as category_name, u.unit_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN units u ON p.unit_id = u.id
        WHERE p.quantity <= p.min_stock_level AND p.status = 'active'
    """)

    low_stock_items = cursor.fetchall()

    for item in low_stock_items:
        # Check if alert already exists
        cursor.execute("""
            SELECT id FROM inventory_alerts
            WHERE product_id = %s AND alert_type = 'low_stock' AND is_read = FALSE
        """, (item['id'],))

        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO inventory_alerts (product_id, alert_type, message)
                VALUES (%s, 'low_stock', %s)
            """, (item['id'], f"Low stock alert: {item['name']} has {item['quantity']} {item['unit_name']} remaining (min: {item['min_stock_level']})"))

    db.commit()
    db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if DEMO_MODE:
        # Demo mode statistics
        total_products = len([p for p in demo_data['products'] if p.get('status', 'active') == 'active'])
        total_categories = len(demo_data['categories'])
        total_suppliers = len(demo_data['suppliers'])
        
        # Generate alerts for low stock items
        active_products = [p for p in demo_data['products'] if p.get('status', 'active') == 'active']
        for product in active_products:
            if product['quantity'] <= product['min_stock_level']:
                # Check if alert already exists
                alert_exists = any(a.get('product_id') == product['id'] and a.get('alert_type') == 'low_stock' 
                                  for a in demo_data['alerts'])
                if not alert_exists:
                    demo_data['alerts'].append({
                        'id': len(demo_data['alerts']) + 1,
                        'product_id': product['id'],
                        'alert_type': 'low_stock',
                        'message': f"Low stock alert: {product['name']} has {product['quantity']} remaining (min: {product['min_stock_level']})",
                        'is_read': False,
                        'created_at': datetime.now()
                    })
        
        total_alerts = len([a for a in demo_data['alerts'] if not a.get('is_read', False)])
        total_value = sum(p['quantity'] * p['cost_price'] for p in active_products)
        low_stock_count = len([p for p in active_products if p['quantity'] <= p['min_stock_level']])

        # Recent movements - use actual demo data if available, otherwise create mock data
        if demo_data['stock_movements']:
            recent_movements = demo_data['stock_movements'][-10:]
        else:
            # Initial mock data for demo
            recent_movements = [
                {'product_name': 'Wireless Mouse', 'movement_type': 'in', 'quantity': 10, 'created_at': datetime.now() - timedelta(hours=2)},
                {'product_name': 'USB-C Cable', 'movement_type': 'out', 'quantity': 5, 'created_at': datetime.now() - timedelta(hours=4)},
                {'product_name': 'Mechanical Keyboard', 'movement_type': 'in', 'quantity': 3, 'created_at': datetime.now() - timedelta(hours=6)},
            ]

        # Get unread alerts (limit to 5)
        alerts = [a for a in demo_data['alerts'] if not a.get('is_read', False)][:5]

        return render_template('dashboard.html',
                             total_products=total_products,
                             total_categories=total_categories,
                             total_suppliers=total_suppliers,
                             total_alerts=total_alerts,
                             total_value=f"{total_value:,.2f}",
                             low_stock_count=low_stock_count,
                             recent_movements=recent_movements,
                             alerts=alerts,
                             demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM products WHERE status = 'active'")
    total_products = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM categories")
    total_categories = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM suppliers")
    total_suppliers = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM inventory_alerts WHERE is_read = FALSE")
    total_alerts = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(quantity * cost_price) as total_value FROM products WHERE status = 'active'")
    total_value = cursor.fetchone()['total_value'] or 0

    # Get low stock items
    cursor.execute("""
        SELECT COUNT(*) as total FROM products
        WHERE quantity <= min_stock_level AND status = 'active'
    """)
    low_stock_count = cursor.fetchone()['total']

    # Get recent stock movements
    cursor.execute("""
        SELECT sm.*, p.name as product_name
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        ORDER BY sm.created_at DESC LIMIT 10
    """)
    recent_movements = cursor.fetchall()

    # Get unread alerts
    cursor.execute("""
        SELECT ia.*, p.name as product_name
        FROM inventory_alerts ia
        JOIN products p ON ia.product_id = p.id
        WHERE ia.is_read = FALSE
        ORDER BY ia.created_at DESC LIMIT 5
    """)
    alerts = cursor.fetchall()

    db.close()

    return render_template('dashboard.html',
                         total_products=total_products,
                         total_categories=total_categories,
                         total_suppliers=total_suppliers,
                         total_alerts=total_alerts,
                         total_value=f"{total_value:,.2f}",
                         low_stock_count=low_stock_count,
                         recent_movements=recent_movements,
                         alerts=alerts,
                         demo_mode=False)

@app.route('/inventory')
@login_required
def inventory():
    if DEMO_MODE:
        # Get filter parameters
        category_id = request.args.get('category')
        search = request.args.get('search', '')
        low_stock = request.args.get('low_stock')

        products = demo_get_products()

        # Apply filters
        if category_id:
            products = [p for p in products if str(p['category_id']) == category_id]

        if search:
            search_lower = search.lower()
            products = [p for p in products if search_lower in p['name'].lower() or search_lower in p['sku'].lower() or search_lower in p['barcode'].lower()]

        if low_stock:
            products = [p for p in products if p['quantity'] <= p['min_stock_level']]

        # Add category, unit, supplier names for display
        categories = demo_get_categories()
        units = demo_get_units()
        suppliers = demo_get_suppliers()

        category_dict = {c['id']: c['name'] for c in categories}
        unit_dict = {u['id']: u['unit_name'] for u in units}
        supplier_dict = {s['id']: s['name'] for s in suppliers}

        for product in products:
            product['category_name'] = category_dict.get(product['category_id'], 'Unknown')
            product['unit_name'] = unit_dict.get(product['unit_id'], 'Unknown')
            product['supplier_name'] = supplier_dict.get(product['supplier_id'], 'Unknown')

        return render_template('inventory.html',
                             products=products,
                             categories=categories,
                             selected_category=category_id,
                             search=search,
                             low_stock=low_stock,
                             demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get filter parameters
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock')

    query = """
        SELECT p.*, c.name as category_name, u.unit_name, s.name as supplier_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN units u ON p.unit_id = u.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE 1=1
    """
    params = []

    if category_id:
        query += " AND p.category_id = %s"
        params.append(category_id)

    if search:
        query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.barcode LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    if low_stock:
        query += " AND p.quantity <= p.min_stock_level"

    query += " ORDER BY p.name"

    cursor.execute(query, params)
    products = cursor.fetchall()

    # Get categories for filter
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    db.close()

    return render_template('inventory.html',
                         products=products,
                         categories=categories,
                         selected_category=category_id,
                         search=search,
                         low_stock=low_stock)

@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        if DEMO_MODE:
            name = request.form['name']
            description = request.form.get('description', '')
            category_id = parse_int_or_none(request.form.get('category_id'))
            unit_id = parse_int_or_none(request.form.get('unit_id'))
            supplier_id = parse_int_or_none(request.form.get('supplier_id'))
            quantity = int(request.form.get('quantity', 0))
            min_stock_level = int(request.form.get('min_stock_level', 0))
            max_stock_level = int(request.form.get('max_stock_level', 0))
            cost_price = float(request.form.get('cost_price', 0))
            selling_price = float(request.form.get('selling_price', 0))
            location = request.form.get('location', '')
            expiry_date = request.form.get('expiry_date') or None
            batch_number = request.form.get('batch_number', '')

            sku = request.form.get('sku') or generate_sku()
            barcode = request.form.get('barcode') or generate_barcode()

            product = {
                'name': name,
                'description': description,
                'category_id': category_id,
                'unit_id': unit_id,
                'supplier_id': supplier_id,
                'sku': sku,
                'barcode': barcode,
                'quantity': quantity,
                'min_stock_level': min_stock_level,
                'max_stock_level': max_stock_level,
                'cost_price': cost_price,
                'selling_price': selling_price,
                'location': location,
                'expiry_date': expiry_date,
                'batch_number': batch_number,
                'status': 'active'
            }

            demo_add_product(product)

            # Record stock movement in demo
            demo_data['stock_movements'].append({
                'product_id': product['id'],
                'movement_type': 'in',
                'quantity': quantity,
                'reason': 'Initial stock',
                'created_at': datetime.now()
            })

            flash('Product added successfully!', 'success')
            check_low_stock()
            return redirect(url_for('inventory'))

        db = get_db()
        cursor = db.cursor()

        name = request.form['name']
        description = request.form.get('description', '')
        category_id = parse_int_or_none(request.form.get('category_id'))
        unit_id = parse_int_or_none(request.form.get('unit_id'))
        supplier_id = parse_int_or_none(request.form.get('supplier_id'))
        quantity = int(request.form.get('quantity', 0))
        min_stock_level = int(request.form.get('min_stock_level', 0))
        max_stock_level = int(request.form.get('max_stock_level', 0))
        cost_price = float(request.form.get('cost_price', 0))
        selling_price = float(request.form.get('selling_price', 0))
        location = request.form.get('location', '')
        expiry_date = request.form.get('expiry_date') or None
        batch_number = request.form.get('batch_number', '')

        sku = request.form.get('sku') or generate_sku()
        barcode = request.form.get('barcode') or generate_barcode()

        try:
            cursor.execute("""
                INSERT INTO products (name, description, category_id, unit_id, supplier_id,
                                   sku, barcode, quantity, min_stock_level, max_stock_level,
                                   cost_price, selling_price, location, expiry_date, batch_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, description, category_id, unit_id, supplier_id, sku, barcode,
                  quantity, min_stock_level, max_stock_level, cost_price, selling_price,
                  location, expiry_date, batch_number))

            product_id = cursor.lastrowid

            # Record stock movement
            cursor.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, reason)
                VALUES (%s, 'in', %s, 'Initial stock')
            """, (product_id, quantity))

            db.commit()
            flash('Product added successfully!', 'success')

            # Check for low stock alerts
            check_low_stock()

        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('inventory'))

    # GET request - show form
    if DEMO_MODE:
        categories = demo_get_categories()
        units = demo_get_units()
        suppliers = demo_get_suppliers()
        return render_template('add_product.html',
                             categories=categories,
                             units=units,
                             suppliers=suppliers,
                             demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM units ORDER BY unit_name")
    units = cursor.fetchall()

    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()

    db.close()

    return render_template('add_product.html',
                         categories=categories,
                         units=units,
                         suppliers=suppliers)

@app.route('/inventory/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if DEMO_MODE:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form.get('description', '')
            category_id = parse_int_or_none(request.form.get('category_id'))
            unit_id = parse_int_or_none(request.form.get('unit_id'))
            supplier_id = parse_int_or_none(request.form.get('supplier_id'))
            min_stock_level = int(request.form.get('min_stock_level', 0))
            max_stock_level = int(request.form.get('max_stock_level', 0))
            cost_price = float(request.form.get('cost_price', 0))
            selling_price = float(request.form.get('selling_price', 0))
            location = request.form.get('location', '')
            expiry_date = request.form.get('expiry_date') or None
            batch_number = request.form.get('batch_number', '')
            status = request.form.get('status', 'active')

            updated_product = {
                'name': name,
                'description': description,
                'category_id': category_id,
                'unit_id': unit_id,
                'supplier_id': supplier_id,
                'min_stock_level': min_stock_level,
                'max_stock_level': max_stock_level,
                'cost_price': cost_price,
                'selling_price': selling_price,
                'location': location,
                'expiry_date': expiry_date,
                'batch_number': batch_number,
                'status': status
            }

            demo_update_product(product_id, updated_product)
            flash('Product updated successfully!', 'success')
            check_low_stock()
            return redirect(url_for('inventory'))

        # GET request - show form with current data
        product = demo_get_product(product_id)
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('inventory'))

        categories = demo_get_categories()
        units = demo_get_units()
        suppliers = demo_get_suppliers()

        return render_template('edit_product.html',
                             product=product,
                             categories=categories,
                             units=units,
                             suppliers=suppliers,
                             demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        category_id = parse_int_or_none(request.form.get('category_id'))
        unit_id = parse_int_or_none(request.form.get('unit_id'))
        supplier_id = parse_int_or_none(request.form.get('supplier_id'))
        min_stock_level = int(request.form.get('min_stock_level', 0))
        max_stock_level = int(request.form.get('max_stock_level', 0))
        cost_price = float(request.form.get('cost_price', 0))
        selling_price = float(request.form.get('selling_price', 0))
        location = request.form.get('location', '')
        expiry_date = request.form.get('expiry_date') or None
        batch_number = request.form.get('batch_number', '')
        status = request.form.get('status', 'active')

        try:
            cursor.execute("""
                UPDATE products SET
                    name=%s, description=%s, category_id=%s, unit_id=%s, supplier_id=%s,
                    min_stock_level=%s, max_stock_level=%s, cost_price=%s, selling_price=%s,
                    location=%s, expiry_date=%s, batch_number=%s, status=%s
                WHERE id=%s
            """, (name, description, category_id, unit_id, supplier_id,
                  min_stock_level, max_stock_level, cost_price, selling_price,
                  location, expiry_date, batch_number, status, product_id))

            db.commit()
            flash('Product updated successfully!', 'success')

            # Check for low stock alerts
            check_low_stock()

        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('inventory'))

    # GET request - show form with current data
    cursor.execute("""
        SELECT * FROM products WHERE id = %s
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('inventory'))

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM units ORDER BY unit_name")
    units = cursor.fetchall()

    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()

    db.close()

    return render_template('edit_product.html',
                         product=product,
                         categories=categories,
                         units=units,
                         suppliers=suppliers)

@app.route('/inventory/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if DEMO_MODE:
        demo_delete_product(product_id)
        flash('Product deleted successfully!', 'success')
        return redirect(url_for('inventory'))

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()
        flash('Product deleted successfully!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('inventory'))

@app.route('/inventory/stock-adjustment/<int:product_id>', methods=['GET', 'POST'])
@login_required
def stock_adjustment(product_id):
    if DEMO_MODE:
        product = demo_get_product(product_id)

        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('inventory'))

        if request.method == 'POST':
            adjustment_type = request.form['adjustment_type']
            quantity = int(request.form['quantity'])
            reason = request.form.get('reason', '')

            if adjustment_type == 'reduce' and quantity > product['quantity']:
                flash('Cannot reduce stock below zero', 'error')
                return redirect(url_for('stock_adjustment', product_id=product_id))

            new_quantity = product['quantity'] + quantity if adjustment_type == 'add' else product['quantity'] - quantity

            try:
                # Update product quantity in demo
                product['quantity'] = new_quantity

                # Record stock movement in demo
                movement_type = 'in' if adjustment_type == 'add' else 'out'
                demo_data['stock_movements'].append({
                    'product_id': product_id,
                    'movement_type': movement_type,
                    'quantity': quantity if adjustment_type == 'add' else -quantity,
                    'reason': reason,
                    'created_at': datetime.now()
                })

                flash('Stock adjusted successfully!', 'success')
                check_low_stock()

            except Exception as e:
                flash(f'Error adjusting stock: {str(e)}', 'error')

            return redirect(url_for('inventory'))

        # Add unit name for display
        units = demo_get_units()
        unit_dict = {u['id']: u['unit_name'] for u in units}
        product['unit_name'] = unit_dict.get(product['unit_id'], 'Unknown')

        return render_template('stock_adjustment.html', product=product, demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get product info
    cursor.execute("""
        SELECT p.*, u.unit_name FROM products p
        LEFT JOIN units u ON p.unit_id = u.id
        WHERE p.id = %s
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('inventory'))

    if request.method == 'POST':
        adjustment_type = request.form['adjustment_type']
        quantity = int(request.form['quantity'])
        reason = request.form.get('reason', '')

        if adjustment_type == 'reduce' and quantity > product['quantity']:
            flash('Cannot reduce stock below zero', 'error')
            db.close()
            return redirect(url_for('stock_adjustment', product_id=product_id))

        new_quantity = product['quantity'] + quantity if adjustment_type == 'add' else product['quantity'] - quantity

        try:
            # Update product quantity
            cursor.execute("UPDATE products SET quantity = %s WHERE id = %s", (new_quantity, product_id))

            # Record stock movement
            movement_type = 'in' if adjustment_type == 'add' else 'adjustment'
            cursor.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, reason)
                VALUES (%s, %s, %s, %s)
            """, (product_id, movement_type, quantity if adjustment_type == 'add' else -quantity, reason))

            db.commit()
            flash('Stock adjusted successfully!', 'success')

            # Check for low stock alerts
            check_low_stock()

        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error adjusting stock: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('inventory'))

    db.close()
    return render_template('stock_adjustment.html', product=product)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        if DEMO_MODE:
            name = request.form.get('cat_name')
            description = request.form.get('description', '')

            # Check if category already exists
            if any(c['name'].lower() == name.lower() for c in demo_data['categories']):
                flash('Category name already exists', 'error')
            else:
                new_id = max(c['id'] for c in demo_data['categories']) + 1 if demo_data['categories'] else 1
                demo_data['categories'].append({
                    'id': new_id,
                    'name': name,
                    'description': description
                })
                flash('Category added successfully!', 'success')
            return redirect(url_for('categories'))

        db = get_db()
        cursor = db.cursor()

        name = request.form.get('cat_name')
        description = request.form.get('description', '')

        try:
            cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, description))
            db.commit()
            flash('Category added successfully!', 'success')
        except mysql.connector.IntegrityError:
            flash('Category name already exists', 'error')
        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error adding category: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('categories'))

    if DEMO_MODE:
        cats = demo_data['categories']
        return render_template('categories.html', categories=cats, demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY name")
    cats = cursor.fetchall()
    db.close()

    return render_template('categories.html', categories=cats)

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if DEMO_MODE:
        # Check if category is being used
        if any(p['category_id'] == category_id for p in demo_data['products']):
            flash('Cannot delete category that is being used by products', 'error')
        else:
            demo_data['categories'] = [c for c in demo_data['categories'] if c['id'] != category_id]
            flash('Category deleted successfully!', 'success')
        return redirect(url_for('categories'))

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if category is being used
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE category_id = %s", (category_id,))
        if cursor.fetchone()['count'] > 0:
            flash('Cannot delete category that is being used by products', 'error')
            db.close()
            return redirect(url_for('categories'))

        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        db.commit()
        flash('Category deleted successfully!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Error deleting category: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('categories'))

@app.route('/units', methods=['GET', 'POST'])
@login_required
def units():
    if request.method == 'POST':
        if DEMO_MODE:
            unit_name = request.form.get('unit_name')
            abbreviation = request.form.get('abbreviation', '')

            # Check if unit already exists
            if any(u['unit_name'].lower() == unit_name.lower() for u in demo_data['units']):
                flash('Unit name already exists', 'error')
            else:
                new_id = max(u['id'] for u in demo_data['units']) + 1 if demo_data['units'] else 1
                demo_data['units'].append({
                    'id': new_id,
                    'unit_name': unit_name,
                    'abbreviation': abbreviation
                })
                flash('Unit added successfully!', 'success')
            return redirect(url_for('units'))

        db = get_db()
        cursor = db.cursor()

        unit_name = request.form.get('unit_name')
        abbreviation = request.form.get('abbreviation', '')

        try:
            cursor.execute("INSERT INTO units (unit_name, abbreviation) VALUES (%s, %s)", (unit_name, abbreviation))
            db.commit()
            flash('Unit added successfully!', 'success')
        except mysql.connector.IntegrityError:
            flash('Unit name already exists', 'error')
        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error adding unit: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('units'))

    if DEMO_MODE:
        unts = demo_data['units']
        return render_template('units.html', units=unts, demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM units ORDER BY unit_name")
    unts = cursor.fetchall()
    db.close()

    return render_template('units.html', units=unts)

@app.route('/units/delete/<int:unit_id>', methods=['POST'])
@login_required
def delete_unit(unit_id):
    if DEMO_MODE:
        # Check if unit is being used
        if any(p['unit_id'] == unit_id for p in demo_data['products']):
            flash('Cannot delete unit that is being used by products', 'error')
        else:
            demo_data['units'] = [u for u in demo_data['units'] if u['id'] != unit_id]
            flash('Unit deleted successfully!', 'success')
        return redirect(url_for('units'))

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if unit is being used
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE unit_id = %s", (unit_id,))
        if cursor.fetchone()['count'] > 0:
            flash('Cannot delete unit that is being used by products', 'error')
            db.close()
            return redirect(url_for('units'))

        cursor.execute("DELETE FROM units WHERE id = %s", (unit_id,))
        db.commit()
        flash('Unit deleted successfully!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Error deleting unit: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('units'))

@app.route('/suppliers')
@login_required
def suppliers():
    if DEMO_MODE:
        suppliers_list = demo_data['suppliers']
        return render_template('suppliers.html', suppliers=suppliers_list, demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers_list = cursor.fetchall()
    db.close()

    return render_template('suppliers.html', suppliers=suppliers_list)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        if DEMO_MODE:
            name = request.form['name']
            contact_person = request.form.get('contact_person', '')
            email = request.form.get('email', '')
            phone = request.form.get('phone', '')
            address = request.form.get('address', '')

            new_id = max(s['id'] for s in demo_data['suppliers']) + 1 if demo_data['suppliers'] else 1
            demo_data['suppliers'].append({
                'id': new_id,
                'name': name,
                'contact_person': contact_person,
                'email': email,
                'phone': phone,
                'address': address
            })
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('suppliers'))

        db = get_db()
        cursor = db.cursor()

        name = request.form['name']
        contact_person = request.form.get('contact_person', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')

        try:
            cursor.execute("""
                INSERT INTO suppliers (name, contact_person, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, contact_person, email, phone, address))
            db.commit()
            flash('Supplier added successfully!', 'success')
        except mysql.connector.Error as e:
            db.rollback()
            flash(f'Error adding supplier: {str(e)}', 'error')
        finally:
            db.close()

        return redirect(url_for('suppliers'))

    return render_template('add_supplier.html', demo_mode=DEMO_MODE)

@app.route('/suppliers/edit/<int:supplier_id>', methods=['POST'])
@login_required
def edit_supplier(supplier_id):
    if DEMO_MODE:
        for supplier in demo_data['suppliers']:
            if supplier['id'] == supplier_id:
                supplier['name'] = request.form['name']
                supplier['contact_person'] = request.form.get('contact_person', '')
                supplier['email'] = request.form.get('email', '')
                supplier['phone'] = request.form.get('phone', '')
                supplier['address'] = request.form.get('address', '')
                break
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers'))

    db = get_db()
    cursor = db.cursor()

    name = request.form['name']
    contact_person = request.form.get('contact_person', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')

    try:
        cursor.execute("""
            UPDATE suppliers SET name=%s, contact_person=%s, email=%s, phone=%s, address=%s
            WHERE id=%s
        """, (name, contact_person, email, phone, address, supplier_id))
        db.commit()
        flash('Supplier updated successfully!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Error updating supplier: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('suppliers'))

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    if DEMO_MODE:
        # Check if supplier is being used
        if any(p['supplier_id'] == supplier_id for p in demo_data['products']):
            flash('Cannot delete supplier that is being used by products', 'error')
        else:
            demo_data['suppliers'] = [s for s in demo_data['suppliers'] if s['id'] != supplier_id]
            flash('Supplier deleted successfully!', 'success')
        return redirect(url_for('suppliers'))

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if supplier is being used
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE supplier_id = %s", (supplier_id,))
        if cursor.fetchone()['count'] > 0:
            flash('Cannot delete supplier that is being used by products', 'error')
            db.close()
            return redirect(url_for('suppliers'))

        cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
        db.commit()
        flash('Supplier deleted successfully!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Error deleting supplier: {str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('suppliers'))

@app.route('/reports')
@login_required
def reports():
    if DEMO_MODE:
        # Demo inventory value report
        inventory_value = []
        category_totals = {}
        for product in demo_data['products']:
            cat_id = product['category_id']
            if cat_id not in category_totals:
                category_totals[cat_id] = {'count': 0, 'value': 0, 'quantity': 0}
            category_totals[cat_id]['count'] += 1
            category_totals[cat_id]['value'] += product['quantity'] * product['cost_price']
            category_totals[cat_id]['quantity'] += product['quantity']

        categories = demo_get_categories()
        for cat_id, totals in category_totals.items():
            cat_name = next((c['name'] for c in categories if c['id'] == cat_id), 'Unknown')
            inventory_value.append({
                'category': cat_name,
                'product_count': totals['count'],
                'total_value': totals['value'],
                'total_quantity': totals['quantity']
            })

        # Demo low stock report
        low_stock = []
        for product in demo_data['products']:
            if product['quantity'] <= product['min_stock_level']:
                cat_name = next((c['name'] for c in categories if c['id'] == product['category_id']), 'Unknown')
                unit_name = next((u['unit_name'] for u in demo_data['units'] if u['id'] == product['unit_id']), 'Unknown')
                low_stock.append({
                    'name': product['name'],
                    'sku': product['sku'],
                    'quantity': product['quantity'],
                    'min_stock_level': product['min_stock_level'],
                    'unit_name': unit_name,
                    'category_name': cat_name
                })

        # Demo stock movements - separate stock_in and stock_out by date
        stock_movements = []
        date_movements = {}
        
        for movement in demo_data['stock_movements']:
            date_key = movement['created_at'].strftime('%Y-%m-%d')
            if date_key not in date_movements:
                date_movements[date_key] = {'month': date_key, 'stock_in': 0, 'stock_out': 0, 'movements': 0}
            
            if movement['movement_type'] == 'in':
                date_movements[date_key]['stock_in'] += abs(movement['quantity'])
            else:
                date_movements[date_key]['stock_out'] += abs(movement['quantity'])
            date_movements[date_key]['movements'] += 1
        
        # Add demo data if no movements exist
        if not date_movements:
            now = datetime.now()
            date_movements = {
                (now - timedelta(days=i)).strftime('%Y-%m-%d'): {
                    'month': (now - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'stock_in': 50 - i*5,
                    'stock_out': 25 - i*2,
                    'movements': 3 + i
                } for i in range(5)
            }
        
        stock_movements = list(date_movements.values())
        stock_movements.sort(key=lambda x: x['month'], reverse=True)

        return render_template('reports.html',
                             inventory_value=inventory_value,
                             low_stock=low_stock,
                             stock_movements=stock_movements,
                             demo_mode=True)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get inventory value report
    cursor.execute("""
        SELECT c.name as category, COUNT(p.id) as product_count,
               SUM(p.quantity * p.cost_price) as total_value,
               SUM(p.quantity) as total_quantity
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.status = 'active'
        GROUP BY c.id, c.name
        ORDER BY total_value DESC
    """)
    inventory_value = cursor.fetchall()

    # Get low stock report
    cursor.execute("""
        SELECT p.name, p.sku, p.quantity, p.min_stock_level, u.unit_name,
               c.name as category_name
        FROM products p
        LEFT JOIN units u ON p.unit_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.quantity <= p.min_stock_level AND p.status = 'active'
        ORDER BY (p.min_stock_level - p.quantity) DESC
    """)
    low_stock = cursor.fetchall()

    # Get stock movement report (last 30 days) - separate inbound and outbound
    cursor.execute("""
        SELECT DATE(sm.created_at) as month,
               SUM(CASE WHEN sm.movement_type = 'in' THEN ABS(sm.quantity) ELSE 0 END) as stock_in,
               SUM(CASE WHEN sm.movement_type IN ('out', 'adjustment') THEN ABS(sm.quantity) ELSE 0 END) as stock_out,
               COUNT(*) as movements
        FROM stock_movements sm
        WHERE sm.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(sm.created_at)
        ORDER BY month DESC
    """)
    stock_movements = cursor.fetchall()

    db.close()

    return render_template('reports.html',
                         inventory_value=inventory_value,
                         low_stock=low_stock,
                         stock_movements=stock_movements)

@app.route('/api/barcode/<barcode>')
@login_required
def get_product_by_barcode(barcode):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, c.name as category_name, u.unit_name, s.name as supplier_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN units u ON p.unit_id = u.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.barcode = %s
    """, (barcode,))

    product = cursor.fetchone()
    db.close()

    if product:
        return jsonify({'success': True, 'product': product})
    else:
        return jsonify({'success': False, 'message': 'Product not found'})

@app.route('/api/alerts/mark-read/<int:alert_id>', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    if DEMO_MODE:
        for alert in demo_data['alerts']:
            if alert['id'] == alert_id:
                alert['is_read'] = True
                break
        return jsonify({'success': True})

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE inventory_alerts SET is_read = TRUE WHERE id = %s", (alert_id,))
        db.commit()
        return jsonify({'success': True})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        db.close()

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get real-time stats
    cursor.execute("SELECT COUNT(*) as total FROM products WHERE status = 'active'")
    total_products = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM inventory_alerts WHERE is_read = FALSE")
    total_alerts = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM products WHERE quantity <= min_stock_level AND status = 'active'")
    low_stock_count = cursor.fetchone()['total']

    db.close()

    return jsonify({
        'total_products': total_products,
        'total_alerts': total_alerts,
        'low_stock_count': low_stock_count
    })

@app.route('/export/inventory')
@login_required
def export_inventory():
    if DEMO_MODE:
        # Demo mode export
        products = demo_get_products()

        # Add category, unit, supplier names for display
        categories = demo_get_categories()
        units = demo_get_units()
        suppliers = demo_get_suppliers()

        category_dict = {c['id']: c['name'] for c in categories}
        unit_dict = {u['id']: u['unit_name'] for u in units}
        supplier_dict = {s['id']: s['name'] for s in suppliers}

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Name', 'SKU', 'Barcode', 'Quantity', 'Cost Price', 'Selling Price',
                        'Category', 'Unit', 'Supplier', 'Location', 'Expiry Date', 'Status'])

        # Write data
        for product in products:
            writer.writerow([
                product['name'], product['sku'], product['barcode'], product['quantity'],
                product['cost_price'], product['selling_price'],
                category_dict.get(product['category_id'], 'Unknown'),
                unit_dict.get(product['unit_id'], 'Unknown'),
                supplier_dict.get(product['supplier_id'], 'Unknown'),
                product.get('location', ''),
                product.get('expiry_date', ''),
                product.get('status', 'active')
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=inventory_export.csv'}
        )

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.name, p.sku, p.barcode, p.quantity, p.cost_price, p.selling_price,
               c.name as category, u.unit_name as unit, s.name as supplier,
               p.location, p.expiry_date, p.status
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN units u ON p.unit_id = u.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.name
    """)

    products = cursor.fetchall()
    db.close()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Name', 'SKU', 'Barcode', 'Quantity', 'Cost Price', 'Selling Price',
                    'Category', 'Unit', 'Supplier', 'Location', 'Expiry Date', 'Status'])

    # Write data
    for product in products:
        writer.writerow([
            product['name'], product['sku'], product['barcode'], product['quantity'],
            product['cost_price'], product['selling_price'], product['category'],
            product['unit'], product['supplier'], product['location'],
            product['expiry_date'], product['status']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=inventory_export.csv'}
    )

# ==================== REAL-TIME ANALYTICS API ENDPOINTS ====================

@app.route('/analytics')
@login_required
def analytics():
    """Main analytics dashboard page"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    dashboard_summary = analytics_engine.get_dashboard_summary()
    trends = analytics_engine.get_trends(30)
    
    return render_template('analytics.html',
                         **dashboard_summary,
                         trends=json.dumps(trends))

@app.route('/api/analytics/kpis')
@login_required
def api_kpis():
    """Get all KPIs in real-time"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    kpis = analytics_engine.get_kpis()
    return jsonify({
        'success': True,
        'data': kpis,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/trends')
@login_required
def api_trends():
    """Get inventory trends"""
    days = request.args.get('days', 30, type=int)
    
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    trends = analytics_engine.get_trends(days)
    return jsonify({
        'success': True,
        'data': trends,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/categories')
@login_required
def api_category_analytics():
    """Get category-wise analytics"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    categories = analytics_engine.get_category_analytics()
    
    # Convert to list of dicts for JSON serialization
    categories_list = []
    for cat in categories:
        categories_list.append({
            'id': cat['id'],
            'category_name': cat['category_name'],
            'product_count': cat['product_count'],
            'total_quantity': cat['total_quantity'],
            'total_value': float(cat['total_value'] or 0),
            'total_selling_value': float(cat['total_selling_value'] or 0),
            'avg_cost': float(cat['avg_cost'] or 0),
            'avg_selling': float(cat['avg_selling'] or 0),
            'min_quantity': cat['min_quantity'],
            'max_quantity': cat['max_quantity'],
        })
    
    return jsonify({
        'success': True,
        'data': categories_list,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/suppliers')
@login_required
def api_supplier_analytics():
    """Get supplier-wise analytics"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    suppliers = analytics_engine.get_supplier_analytics()
    
    # Convert to list of dicts for JSON serialization
    suppliers_list = []
    for sup in suppliers:
        suppliers_list.append({
            'id': sup['id'],
            'supplier_name': sup['supplier_name'],
            'product_count': sup['product_count'],
            'total_quantity': sup['total_quantity'],
            'total_value': float(sup['total_value'] or 0),
            'avg_cost': float(sup['avg_cost'] or 0),
            'total_shipments': sup['total_shipments'],
        })
    
    return jsonify({
        'success': True,
        'data': suppliers_list,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/top-products')
@login_required
def api_top_products():
    """Get top products by various metrics"""
    metric = request.args.get('metric', 'value')
    limit = request.args.get('limit', 10, type=int)
    
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    products = analytics_engine.get_top_products(limit, metric)
    
    # Convert to list of dicts for JSON serialization
    products_list = []
    for prod in products:
        products_list.append({
            'id': prod['id'],
            'name': prod['name'],
            'sku': prod['sku'],
            'quantity': prod['quantity'],
            'cost_price': float(prod['cost_price']),
            'selling_price': float(prod['selling_price']),
            'category_name': prod.get('category_name', 'N/A'),
            'total_value': float(prod.get('total_value', 0)),
            'profit_margin': float(prod.get('profit_margin', 0)),
        })
    
    return jsonify({
        'success': True,
        'data': products_list,
        'metric': metric,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/profit-analysis')
@login_required
def api_profit_analysis():
    """Get profit and margin analysis"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    profit_data = analytics_engine.get_profit_analysis()
    return jsonify({
        'success': True,
        'data': {
            'total_cost': float(profit_data['total_cost']),
            'total_selling_value': float(profit_data['total_selling_value']),
            'total_profit': float(profit_data['total_profit']),
            'avg_margin_percent': float(profit_data['avg_margin_percent']),
            'profit_margin': float(profit_data['profit_margin']),
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/alerts')
@login_required
def api_get_alerts():
    """Get critical alerts in real-time"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    alerts = analytics_engine.get_critical_alerts()
    
    # Convert to list of dicts for JSON serialization
    alerts_list = []
    for alert in alerts:
        alerts_list.append({
            'id': alert['id'],
            'name': alert['name'],
            'alert_type': alert['alert_type'],
            'message': alert['message'],
            'quantity': alert.get('quantity', 0),
        })
    
    return jsonify({
        'success': True,
        'data': alerts_list,
        'alert_count': len(alerts_list),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/dashboard-summary')
@login_required
def api_dashboard_summary():
    """Get complete dashboard summary"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    summary = analytics_engine.get_dashboard_summary()
    
    # Helper function to convert Decimal to float
    def convert_decimals(obj):
        if isinstance(obj, dict):
            return {k: convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_decimals(item) for item in obj]
        elif hasattr(obj, '__float__'):
            return float(obj)
        else:
            return obj
    
    summary = convert_decimals(summary)
    
    return jsonify({
        'success': True,
        'data': summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/export-report')
@login_required
def api_export_analytics_report():
    """Export analytics report as JSON"""
    if DEMO_MODE:
        analytics_engine = InventoryAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        analytics_engine = InventoryAnalytics(db_connection=db)
    
    # Helper function to convert Decimal to float
    def convert_decimals(obj):
        if isinstance(obj, dict):
            return {k: convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_decimals(item) for item in obj]
        elif hasattr(obj, '__float__'):
            return float(obj)
        else:
            return obj
    
    report_data = {
        'kpis': analytics_engine.get_kpis(),
        'trends': analytics_engine.get_trends(30),
        'category_analytics': analytics_engine.get_category_analytics(),
        'supplier_analytics': analytics_engine.get_supplier_analytics(),
        'top_products': analytics_engine.get_top_products(limit=10),
        'profit_analysis': analytics_engine.get_profit_analysis(),
        'critical_alerts': analytics_engine.get_critical_alerts(),
        'export_date': datetime.now().isoformat(),
    }
    
    report_data = convert_decimals(report_data)
    
    return jsonify(report_data)

# ==================== PREDICTIVE ANALYTICS API ENDPOINTS ====================

@app.route('/api/predictions/demand-forecast/<int:product_id>')
@login_required
def api_demand_forecast(product_id):
    """Get demand forecast for a product"""
    days = request.args.get('days', 30, type=int)
    
    if DEMO_MODE:
        predictor = PredictiveAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        predictor = PredictiveAnalytics(db_connection=db)
    
    forecast_data = predictor.forecast_demand(product_id, days)
    
    if forecast_data:
        return jsonify({
            'success': True,
            'data': forecast_data,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Product not found'
        }), 404

@app.route('/api/predictions/reorder-point/<int:product_id>')
@login_required
def api_reorder_point(product_id):
    """Get reorder point calculation for a product"""
    if DEMO_MODE:
        predictor = PredictiveAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        predictor = PredictiveAnalytics(db_connection=db)
    
    reorder_data = predictor.calculate_reorder_point(product_id)
    
    if reorder_data:
        return jsonify({
            'success': True,
            'data': reorder_data,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Product not found'
        }), 404

@app.route('/api/predictions/expiry-impact')
@login_required
def api_expiry_impact():
    """Get expiry impact predictions"""
    if DEMO_MODE:
        predictor = PredictiveAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        predictor = PredictiveAnalytics(db_connection=db)
    
    expiry_data = predictor.predict_expiry_impact()
    return jsonify({
        'success': True,
        'data': expiry_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predictions/seasonal-patterns')
@login_required
def api_seasonal_patterns():
    """Get seasonal pattern analysis"""
    product_id = request.args.get('product_id', type=int)
    
    if DEMO_MODE:
        predictor = PredictiveAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        predictor = PredictiveAnalytics(db_connection=db)
    
    patterns = predictor.analyze_seasonal_patterns(product_id)
    return jsonify({
        'success': True,
        'data': patterns,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predictions/all')
@login_required
def api_all_predictions():
    """Get comprehensive prediction report"""
    if DEMO_MODE:
        predictor = PredictiveAnalytics(demo_data=demo_data)
    else:
        db = get_db()
        predictor = PredictiveAnalytics(db_connection=db)
    
    predictions = predictor.get_all_predictions()
    return jsonify({
        'success': True,
        'data': predictions,
        'timestamp': datetime.now().isoformat()
    })

# ==================== REAL-TIME ALERT API ENDPOINTS ====================

@app.route('/api/alerts/all')
@login_required
def api_get_all_alerts():
    """Get all active alerts in real-time"""
    if DEMO_MODE:
        alert_system = RealtimeAlertSystem(demo_data=demo_data)
    else:
        db = get_db()
        alert_system = RealtimeAlertSystem(db_connection=db)
    
    alerts = alert_system.get_all_alerts()
    return jsonify({
        'success': True,
        'data': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/critical')
@login_required
def api_get_critical_alerts():
    """Get only critical alerts"""
    if DEMO_MODE:
        alert_system = RealtimeAlertSystem(demo_data=demo_data)
    else:
        db = get_db()
        alert_system = RealtimeAlertSystem(db_connection=db)
    
    alerts = alert_system.get_critical_alerts()
    return jsonify({
        'success': True,
        'data': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/summary')
@login_required
def api_alerts_summary():
    """Get alerts summary"""
    if DEMO_MODE:
        alert_system = RealtimeAlertSystem(demo_data=demo_data)
    else:
        db = get_db()
        alert_system = RealtimeAlertSystem(db_connection=db)
    
    summary = alert_system.get_alert_summary()
    return jsonify({
        'success': True,
        'data': summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/check-stock')
@login_required
def api_check_stock_alerts():
    """Check stock level alerts"""
    if DEMO_MODE:
        alert_system = RealtimeAlertSystem(demo_data=demo_data)
    else:
        db = get_db()
        alert_system = RealtimeAlertSystem(db_connection=db)
    
    alerts = alert_system.check_stock_levels()
    return jsonify({
        'success': True,
        'data': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/check-expiry')
@login_required
def api_check_expiry_alerts():
    """Check expiry alerts"""
    if DEMO_MODE:
        alert_system = RealtimeAlertSystem(demo_data=demo_data)
    else:
        db = get_db()
        alert_system = RealtimeAlertSystem(db_connection=db)
    
    alerts = alert_system.check_expiry_alerts()
    return jsonify({
        'success': True,
        'data': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

# ==================== ACTIVITY & RECENT ACTIONS API ====================

@app.route('/api/activity/recent')
@login_required
def api_recent_activity():
    """Get recent stock movements and activity"""
    limit = request.args.get('limit', 10, type=int)
    
    if DEMO_MODE:
        # Demo mode: return recent stock movements
        recent_activities = demo_data['stock_movements'][-limit:] if demo_data['stock_movements'] else []
        
        # Format for API response
        activities = []
        for activity in reversed(recent_activities):
            activities.append({
                'product_id': activity.get('product_id', 0),
                'product_name': next((p['name'] for p in demo_data['products'] if p['id'] == activity.get('product_id')), 'Unknown'),
                'movement_type': activity.get('movement_type', 'unknown'),
                'quantity': activity.get('quantity', 0),
                'reason': activity.get('reason', 'Stock adjustment'),
                'timestamp': activity.get('created_at', datetime.now()).isoformat() if isinstance(activity.get('created_at'), datetime) else str(activity.get('created_at')),
                'created_at': activity.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'data': activities,
            'count': len(activities),
            'timestamp': datetime.now().isoformat()
        })
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT sm.*, p.name as product_name
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        ORDER BY sm.created_at DESC
        LIMIT %s
    """, (limit,))
    
    activities = cursor.fetchall()
    db.close()
    
    return jsonify({
        'success': True,
        'data': activities,
        'count': len(activities) if activities else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/activity/log', methods=['POST'])
@login_required
def api_log_activity():
    """Log an activity event (for tracking user actions)"""
    if DEMO_MODE:
        # In demo mode, just return success
        return jsonify({
            'success': True,
            'message': 'Activity logged (demo mode)'
        })
    
    data = request.get_json()
    action_type = data.get('action_type', 'unknown')
    description = data.get('description', '')
    product_id = data.get('product_id')
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO activity_log (action_type, description, product_id, user_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (action_type, description, product_id, session.get('user_id', 1)))
        
        db.commit()
        return jsonify({
            'success': True,
            'message': 'Activity logged successfully'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'Error logging activity: {str(e)}'
        }), 400
    finally:
        db.close()

@app.route('/api/activity/stats')
@login_required
def api_activity_stats():
    """Get activity statistics (movements count, etc)"""
    if DEMO_MODE:
        stock_movements = demo_data['stock_movements']
        return jsonify({
            'success': True,
            'data': {
                'total_movements': len(stock_movements),
                'inbound': len([m for m in stock_movements if m.get('movement_type') == 'in']),
                'outbound': len([m for m in stock_movements if m.get('movement_type') in ['out', 'adjustment']]),
                'last_movement': stock_movements[-1].get('created_at').isoformat() if stock_movements else None
            },
            'timestamp': datetime.now().isoformat()
        })
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_movements,
            SUM(CASE WHEN movement_type = 'in' THEN 1 ELSE 0 END) as inbound,
            SUM(CASE WHEN movement_type IN ('out', 'adjustment') THEN 1 ELSE 0 END) as outbound,
            MAX(created_at) as last_movement
        FROM stock_movements
    """)
    
    stats = cursor.fetchone()
    db.close()
    
    return jsonify({
        'success': True,
        'data': {
            'total_movements': stats['total_movements'] or 0,
            'inbound': stats['inbound'] or 0,
            'outbound': stats['outbound'] or 0,
            'last_movement': stats['last_movement'].isoformat() if stats['last_movement'] else None
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')