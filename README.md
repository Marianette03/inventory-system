# Advanced Inventory Management System

A comprehensive, professional-grade inventory management system built with Flask, MySQL, and modern web technologies. Features advanced analytics, barcode scanning, real-time monitoring, and automated alerts.

## 🚀 Features

### Core Functionality
- **Complete CRUD Operations**: Full Create, Read, Update, Delete for all inventory items
- **Multi-User Support**: Session-based authentication with role management
- **Real-Time Dashboard**: Live inventory statistics and alerts
- **Advanced Search & Filtering**: Powerful search across all inventory data
- **Stock Movement Tracking**: Complete audit trail of inventory changes
- **Supplier Management**: Comprehensive supplier database and tracking

### Advanced Features
- **Barcode Scanning**: Integrated barcode scanning with camera support
- **Predictive Analytics**: AI-powered stock level predictions and trends
- **Automated Alerts**: Smart low-stock and expiry date notifications
- **Comprehensive Reporting**: Detailed reports with charts and export options
- **Data Export**: CSV export for all inventory data and reports
- **Responsive Design**: Mobile-first design that works on all devices

### Technical Features
- **RESTful API**: Complete API for integrations and mobile apps
- **Real-Time Updates**: WebSocket-based live data updates
- **Advanced Analytics**: Charts and graphs for inventory insights
- **Keyboard Shortcuts**: Productivity-enhancing shortcuts
- **Modal Interfaces**: Modern, non-intrusive user interactions

## 🛠️ Technology Stack

- **Backend**: Python Flask with RESTful API
- **Database**: MySQL/MariaDB with optimized schema
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Charts**: Chart.js for data visualization
- **Styling**: Modern CSS with glassmorphism effects
- **Responsive**: Mobile-first responsive design

## 📋 Prerequisites

- Python 3.6 or higher
- MySQL 5.7+ or MariaDB 10.0+
- Modern web browser with camera support (for barcode scanning)
- Git (for cloning the repository)

## 🚀 Quick Start

### Option 1: Demo Mode (Recommended for Testing)

If you don't have MySQL installed, use demo mode which runs entirely in memory:

```bash
git clone <repository-url>
cd inventory-system
pip install -r requirements.txt
python demo.py
```

**Demo Mode Features:**
- No database required
- Sample data pre-loaded
- All features fully functional
- Perfect for testing and evaluation

### Option 2: Full Database Mode

For production use with MySQL:

#### 1. Install MySQL
Download and install MySQL Community Server from:
https://dev.mysql.com/downloads/mysql/

Or use XAMPP: https://www.apachefriends.org/

#### 2. Setup the System
```bash
git clone <repository-url>
cd inventory-system
pip install -r requirements.txt
python setup.py
```

#### 3. Run the Application
```bash
python backend/app.py
```

### 4. Access the System
Open your browser and navigate to: `http://localhost:5000`

**Default Login Credentials:**
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
inventory-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   └── README.md             # Backend documentation
├── db/
│   ├── schema.sgl            # Database schema
│   └── README.md             # Database documentation
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Main stylesheet
│   │   └── js/
│   │       └── main.js       # Frontend JavaScript
│   ├── templates/            # Jinja2 templates
│   │   ├── layout.html       # Base template
│   │   ├── dashboard.html    # Main dashboard
│   │   ├── inventory.html    # Inventory management
│   │   ├── categories.html   # Category management
│   │   ├── units.html        # Unit management
│   │   ├── suppliers.html    # Supplier management
│   │   ├── add_product.html  # Add product form
│   │   ├── edit_product.html # Edit product form
│   │   ├── stock_adjustment.html # Stock adjustment
│   │   ├── reports.html      # Reports and analytics
│   │   └── add_supplier.html # Add supplier form
├── setup.py                  # Database setup script
├── demo.py                   # Demo mode runner
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Database Configuration
Edit the database settings in `backend/app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'inventory_db'
}
```

### Application Settings
Modify application settings in `backend/app.py`:

```python
# Flask configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'
```

## 📊 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /logout` - User logout

### Products
- `GET /api/products` - Get all products
- `POST /api/products` - Create new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `GET /api/products/<id>` - Get product details

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create category
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category

### Suppliers
- `GET /api/suppliers` - Get all suppliers
- `POST /api/suppliers` - Create supplier
- `PUT /api/suppliers/<id>` - Update supplier
- `DELETE /api/suppliers/<id>` - Delete supplier

### Analytics & Reports
- `GET /api/dashboard-data` - Dashboard statistics
- `GET /api/analytics` - Analytics data
- `GET /api/reports/stock-movements` - Stock movement reports
- `GET /api/reports/low-stock` - Low stock alerts

### Barcode & Utilities
- `POST /api/barcode/scan` - Process barcode scan
- `GET /api/export/<type>` - Export data as CSV

## 🎯 Usage Guide

### Dashboard
- View real-time inventory statistics
- Monitor low stock alerts
- Access quick actions and shortcuts

### Inventory Management
- Add, edit, and delete products
- Track stock levels and movements
- Set minimum and maximum stock levels
- Manage product categories and units

### Supplier Management
- Maintain supplier database
- Track supplier performance
- Manage supplier contacts and information

### Reports & Analytics
- Generate detailed inventory reports
- View trend analysis and predictions
- Export data for external analysis
- Monitor stock movement history

### Barcode Integration
- Scan barcodes using device camera
- Automatic product lookup and updates
- Support for various barcode formats

## 🔐 Security Features

- Session-based authentication
- CSRF protection
- SQL injection prevention
- Input validation and sanitization
- Secure password handling
- Role-based access control

## 📱 Mobile Support

- Responsive design for all screen sizes
- Touch-friendly interface
- Mobile-optimized forms and tables
- Camera integration for barcode scanning

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python backend/app.py
```

### Database Migrations
If you need to modify the database schema:
1. Update `db/schema.sgl`
2. Run the setup script again: `python setup.py`

### Adding New Features
1. Backend changes in `backend/app.py`
2. Frontend templates in `frontend/templates/`
3. Styles in `frontend/static/css/style.css`
4. JavaScript in `frontend/static/js/main.js`

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Ensure MySQL/MariaDB is running
- Check database credentials in `backend/app.py`
- Use demo mode: `python demo.py`

**Port Already in Use**
- Change the port in `backend/app.py`: `app.run(port=5001)`

**Barcode Scanning Not Working**
- Ensure HTTPS for camera access
- Check browser camera permissions
- Verify camera hardware is available

**Import Errors**
- Install all requirements: `pip install -r requirements.txt`
- Check Python version compatibility

### Demo Mode Issues
- Demo mode doesn't save data permanently
- All changes are lost when server restarts
- Use full database mode for persistent data

### Logs and Debugging
- Check console for JavaScript errors
- View Flask logs in terminal
- Enable debug mode: `app.run(debug=True)`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## 🔄 Updates

### Version 2.0.0 - Enhanced Edition
- Complete inventory management system
- Advanced analytics and reporting
- Barcode scanning integration
- Real-time dashboard
- Mobile-responsive design
- **NEW**: Demo mode for easy testing
- **NEW**: Enhanced UI with modern design
- **NEW**: Comprehensive supplier management
- **NEW**: Stock movement tracking
- **NEW**: Automated alerts system
- **NEW**: Export functionality
- **NEW**: Keyboard shortcuts
- **NEW**: Modal interfaces

---

**Built with ❤️ for efficient inventory management**