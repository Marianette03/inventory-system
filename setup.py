#!/usr/bin/env python3
"""
INVENTORY SYSTEM SETUP SCRIPT
Enhanced Inventory Management System with Advanced Features
"""

import mysql.connector
import os
import sys
from pathlib import Path

def create_database_and_tables():
    """Create database and tables if they don't exist"""

    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
    }

    try:
        # Connect without specifying database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
        print("✓ Database 'inventory_db' created successfully")

        # Switch to the database
        cursor.execute("USE inventory_db")

        # Read and execute schema
        schema_path = Path(__file__).parent / 'db' / 'schema.sgl'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Split SQL commands and execute them
        commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]

        for command in commands:
            if command:
                try:
                    cursor.execute(command)
                except mysql.connector.Error as e:
                    if 'Duplicate entry' not in str(e):
                        print(f"Warning: {e}")

        conn.commit()
        print("✓ Database tables created successfully")

        # Insert sample data
        insert_sample_data(cursor)
        conn.commit()

        cursor.close()
        conn.close()

        print("✓ Database setup completed successfully!")
        print("\n" + "="*50)
        print("INVENTORY SYSTEM READY")
        print("="*50)
        print("Login Credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\nFeatures:")
        print("• Complete CRUD operations for products")
        print("• Supplier management")
        print("• Stock movement tracking")
        print("• Low stock alerts")
        print("• Advanced reporting & analytics")
        print("• Barcode scanning support")
        print("• Export functionality")
        print("• Real-time dashboard")
        print("="*50)

    except FileNotFoundError:
        print("✗ Schema file not found. Make sure schema.sgl exists in db/ directory")
        sys.exit(1)
    except mysql.connector.Error as e:
        print(f"✗ Database error: {e}")
        print("\n" + "="*50)
        print("MYSQL INSTALLATION REQUIRED")
        print("="*50)
        print("To install MySQL on Windows:")
        print("1. Download MySQL Installer from:")
        print("   https://dev.mysql.com/downloads/mysql/")
        print("2. Run the installer and select 'Developer Default' setup")
        print("3. Set root password to empty (no password) during installation")
        print("4. Complete the installation")
        print("5. Start MySQL service from Windows Services")
        print("6. Run this setup script again")
        print("\nAlternative: Use XAMPP which includes MySQL")
        print("1. Download XAMPP: https://www.apachefriends.org/")
        print("2. Install and start MySQL from XAMPP control panel")
        print("="*50)
        sys.exit(1)


def insert_sample_data(cursor):
    """Insert sample data for demonstration"""

    # Sample suppliers
    suppliers = [
        ('TechCorp Supplies', 'John Smith', 'john@techcorp.com', '+63 912 345 6789', '123 Business St, Makati City'),
        ('Global Electronics', 'Maria Garcia', 'maria@globalelec.com', '+63 917 987 6543', '456 Commerce Ave, BGC'),
        ('Office Solutions Inc', 'Robert Chen', 'robert@officesol.com', '+63 922 111 2222', '789 Corporate Blvd, Ortigas'),
    ]

    cursor.executemany("""
        INSERT IGNORE INTO suppliers (name, contact_person, email, phone, address)
        VALUES (%s, %s, %s, %s, %s)
    """, suppliers)

    # Sample categories
    categories = [
        ('Electronics', 'Electronic devices and components'),
        ('Hardware', 'Computer hardware and peripherals'),
        ('Software', 'Software licenses and digital products'),
        ('Accessories', 'Various accessories and peripherals'),
        ('Consumables', 'Consumable items and supplies'),
        ('Furniture', 'Office furniture and equipment'),
        ('Tools', 'Tools and maintenance equipment'),
    ]

    cursor.executemany("""
        INSERT IGNORE INTO categories (name, description)
        VALUES (%s, %s)
    """, categories)

    # Sample units
    units = [
        ('Pieces', 'pcs'),
        ('Kilograms', 'kg'),
        ('Liters', 'L'),
        ('Boxes', 'box'),
        ('Meters', 'm'),
        ('Packets', 'pkt'),
        ('Sets', 'set'),
        ('Dozen', 'dz'),
        ('Rolls', 'roll'),
    ]

    cursor.executemany("""
        INSERT IGNORE INTO units (unit_name, abbreviation)
        VALUES (%s, %s)
    """, units)

    # Sample products
    products = [
        ('Wireless Mouse', 'Ergonomic wireless optical mouse', 1, 1, 1, 'MS-001', '123456789012', 45, 10, 100, 450.00, 650.00, 'Shelf A1', None, 'BT-001'),
        ('Mechanical Keyboard', 'RGB backlit mechanical gaming keyboard', 1, 1, 1, 'KB-001', '123456789013', 12, 5, 50, 2500.00, 3200.00, 'Shelf A2', None, 'MK-001'),
        ('USB-C Cable', '1m braided USB-C to USB-C cable', 1, 1, 1, 'CB-001', '123456789014', 78, 20, 200, 150.00, 250.00, 'Shelf B1', None, 'UC-001'),
        ('External Hard Drive', '2TB portable external HDD', 1, 1, 2, 'HD-001', '123456789015', 8, 3, 25, 3500.00, 4200.00, 'Shelf A3', None, 'EH-001'),
        ('Office Chair', 'Ergonomic office chair with lumbar support', 6, 1, 3, 'CH-001', '123456789016', 15, 5, 30, 8500.00, 12000.00, 'Warehouse 1', None, 'OC-001'),
        ('Printer Paper', 'A4 size, 500 sheets per pack', 5, 6, 3, 'PP-001', '123456789017', 25, 10, 100, 180.00, 250.00, 'Storage Room', None, 'PP-001'),
        ('Network Cable', 'Cat6 Ethernet cable, 10m', 1, 5, 1, 'NC-001', '123456789018', 32, 15, 80, 320.00, 450.00, 'Shelf C1', None, 'C6-001'),
        ('Webcam', '1080p HD webcam with microphone', 1, 1, 2, 'WC-001', '123456789019', 6, 3, 20, 1200.00, 1800.00, 'Shelf A4', None, 'WC-001'),
    ]

    cursor.executemany("""
        INSERT IGNORE INTO products
        (name, description, category_id, unit_id, supplier_id, sku, barcode,
         quantity, min_stock_level, max_stock_level, cost_price, selling_price,
         location, expiry_date, batch_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, products)

    print("✓ Sample data inserted successfully")


def check_requirements():
    """Check if all requirements are met"""
    print("Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 6):
        print("✗ Python 3.6 or higher is required")
        sys.exit(1)
    print("✓ Python version:", sys.version.split()[0])

    # Check if required modules are available
    try:
        import flask
        print("✓ Flask version:", flask.__version__)
    except ImportError:
        print("✗ Flask is not installed. Run: pip install flask")
        sys.exit(1)

    try:
        import mysql.connector
        print("✓ MySQL Connector available")
    except ImportError:
        print("✗ MySQL Connector is not installed. Run: pip install mysql-connector-python")
        sys.exit(1)

    # Check if database files exist
    schema_file = Path(__file__).parent / 'db' / 'schema.sgl'
    if not schema_file.exists():
        print("✗ Database schema file not found")
        sys.exit(1)
    print("✓ Database schema file found")

    print("All requirements met!\n")


def main():
    """Main setup function"""
    print("\n" + "="*50)
    print("INVENTORY SYSTEM SETUP")
    print("="*50 + "\n")

    check_requirements()
    create_database_and_tables()


if __name__ == "__main__":
    main()
