"""
Analytics Module for Real-Time Inventory Analytics and Reporting
Provides comprehensive analytics, KPIs, trends, and insights
"""

from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class InventoryAnalytics:
    """Main analytics class for inventory system"""
    
    def __init__(self, db_connection=None, demo_data=None):
        self.db = db_connection
        self.demo_data = demo_data
        self.is_demo = demo_data is not None
    
    # ==================== KPI CALCULATIONS ====================
    
    def get_kpis(self):
        """Calculate all key performance indicators"""
        if self.is_demo:
            return self._get_demo_kpis()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            kpis = {
                'total_inventory_value': self._calculate_total_value(cursor),
                'total_products': self._count_active_products(cursor),
                'low_stock_items': self._count_low_stock_items(cursor),
                'out_of_stock_items': self._count_out_of_stock_items(cursor),
                'expiring_soon': self._count_expiring_items(cursor),
                'movement_rate': self._calculate_movement_rate(cursor),
                'inventory_turnover': self._calculate_turnover_ratio(cursor),
                'stock_accuracy': self._calculate_stock_accuracy(cursor),
            }
            return kpis
        finally:
            cursor.close()
    
    def _calculate_total_value(self, cursor):
        """Calculate total inventory value"""
        cursor.execute("""
            SELECT COALESCE(SUM(p.quantity * p.cost_price), 0) as total_value
            FROM products p
            WHERE p.status = 'active'
        """)
        result = cursor.fetchone()
        return float(result['total_value']) if result else 0.0
    
    def _count_active_products(self, cursor):
        """Count active products"""
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _count_low_stock_items(self, cursor):
        """Count items with low stock"""
        cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE quantity > 0 AND quantity <= min_stock_level AND status = 'active'
        """)
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _count_out_of_stock_items(self, cursor):
        """Count out of stock items"""
        cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE quantity = 0 AND status = 'active'
        """)
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _count_expiring_items(self, cursor):
        """Count items expiring within 30 days"""
        cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE expiry_date IS NOT NULL AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            AND expiry_date >= CURDATE() AND status = 'active'
        """)
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _calculate_movement_rate(self, cursor):
        """Calculate average daily movement rate (items per day)"""
        cursor.execute("""
            SELECT AVG(daily_movement) as avg_movement
            FROM (
                SELECT DATE(created_at) as date, SUM(ABS(quantity)) as daily_movement
                FROM stock_movements
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
            ) as daily_movements
        """)
        result = cursor.fetchone()
        return float(result['avg_movement']) if result and result['avg_movement'] else 0.0
    
    def _calculate_turnover_ratio(self, cursor):
        """Calculate inventory turnover ratio"""
        cursor.execute("""
            SELECT SUM(COGS) / NULLIF(AVG(inventory_value), 0) as turnover
            FROM (
                SELECT 
                    (SELECT COALESCE(SUM(quantity * cost_price), 0) FROM products WHERE status = 'active') as inventory_value,
                    (SELECT COALESCE(SUM(ABS(quantity) * 
                        (SELECT cost_price FROM products p WHERE p.id = sm.product_id)), 0)
                     FROM stock_movements sm
                     WHERE movement_type = 'out' AND sm.created_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                    ) as COGS
            ) as metrics
        """)
        result = cursor.fetchone()
        return float(result['turnover']) if result and result['turnover'] else 0.0
    
    def _calculate_stock_accuracy(self, cursor):
        """Calculate stock counting accuracy percentage"""
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN quantity >= min_stock_level THEN 1 END) as compliant
            FROM products WHERE status = 'active'
        """)
        result = cursor.fetchone()
        if result and result['total'] > 0:
            return (result['compliant'] / result['total']) * 100
        return 0.0
    
    def _get_demo_kpis(self):
        """Get demo KPIs"""
        products = self.demo_data.get('products', [])
        active_products = [p for p in products if p.get('status', 'active') == 'active']
        
        total_value = sum(p['quantity'] * p['cost_price'] for p in active_products)
        low_stock = sum(1 for p in active_products if 0 < p['quantity'] <= p['min_stock_level'])
        out_of_stock = sum(1 for p in active_products if p['quantity'] == 0)
        
        return {
            'total_inventory_value': total_value,
            'total_products': len(active_products),
            'low_stock_items': low_stock,
            'out_of_stock_items': out_of_stock,
            'expiring_soon': 0,
            'movement_rate': 15.5,
            'inventory_turnover': 4.2,
            'stock_accuracy': 94.5,
        }
    
    # ==================== TREND ANALYSIS ====================
    
    def get_trends(self, days=30):
        """Get inventory trends for specified number of days"""
        if self.is_demo:
            return self._get_demo_trends(days)
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Stock movement trends
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    movement_type,
                    SUM(ABS(quantity)) as total_quantity,
                    COUNT(*) as movement_count
                FROM stock_movements
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(created_at), movement_type
                ORDER BY date ASC
            """, (days,))
            
            movements = cursor.fetchall()
            
            # Organization by type
            trends = defaultdict(list)
            for movement in movements:
                trends[movement['movement_type']].append({
                    'date': str(movement['date']),
                    'quantity': movement['total_quantity'],
                    'count': movement['movement_count']
                })
            
            return dict(trends)
        finally:
            cursor.close()
    
    def _get_demo_trends(self, days):
        """Get demo trends"""
        import random
        trends = {'in': [], 'out': [], 'adjustment': []}
        start_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            if date.weekday() < 5:  # Weekdays only
                trends['in'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'quantity': random.randint(50, 150),
                    'count': random.randint(2, 8)
                })
                trends['out'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'quantity': random.randint(30, 100),
                    'count': random.randint(1, 5)
                })
        
        return trends
    
    # ==================== CATEGORY ANALYTICS ====================
    
    def get_category_analytics(self):
        """Get detailed analytics by category"""
        if self.is_demo:
            return self._get_demo_category_analytics()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name as category_name,
                    COUNT(p.id) as product_count,
                    SUM(p.quantity) as total_quantity,
                    SUM(p.quantity * p.cost_price) as total_value,
                    SUM(p.quantity * p.selling_price) as total_selling_value,
                    AVG(p.cost_price) as avg_cost,
                    AVG(p.selling_price) as avg_selling,
                    MIN(p.quantity) as min_quantity,
                    MAX(p.quantity) as max_quantity
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.status = 'active'
                GROUP BY c.id, c.name
                ORDER BY total_value DESC
            """)
            
            categories = cursor.fetchall()
            return categories
        finally:
            cursor.close()
    
    def _get_demo_category_analytics(self):
        """Get demo category analytics"""
        categories = self.demo_data.get('categories', [])
        products = [p for p in self.demo_data.get('products', []) if p.get('status', 'active') == 'active']
        
        analytics = []
        for cat in categories:
            cat_products = [p for p in products if p['category_id'] == cat['id']]
            if cat_products:
                analytics.append({
                    'id': cat['id'],
                    'category_name': cat['name'],
                    'product_count': len(cat_products),
                    'total_quantity': sum(p['quantity'] for p in cat_products),
                    'total_value': sum(p['quantity'] * p['cost_price'] for p in cat_products),
                    'total_selling_value': sum(p['quantity'] * p['selling_price'] for p in cat_products),
                    'avg_cost': sum(p['cost_price'] for p in cat_products) / len(cat_products),
                    'avg_selling': sum(p['selling_price'] for p in cat_products) / len(cat_products),
                    'min_quantity': min(p['quantity'] for p in cat_products),
                    'max_quantity': max(p['quantity'] for p in cat_products),
                })
        
        return analytics
    
    # ==================== SUPPLIER ANALYTICS ====================
    
    def get_supplier_analytics(self):
        """Get analytics by supplier"""
        if self.is_demo:
            return self._get_demo_supplier_analytics()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name as supplier_name,
                    COUNT(p.id) as product_count,
                    SUM(p.quantity) as total_quantity,
                    SUM(p.quantity * p.cost_price) as total_value,
                    AVG(p.cost_price) as avg_cost,
                    COUNT(DISTINCT sm.id) as total_shipments
                FROM suppliers s
                LEFT JOIN products p ON s.id = p.supplier_id AND p.status = 'active'
                LEFT JOIN stock_movements sm ON p.id = sm.product_id AND sm.movement_type = 'in'
                GROUP BY s.id, s.name
                ORDER BY total_value DESC
            """)
            
            suppliers = cursor.fetchall()
            return suppliers
        finally:
            cursor.close()
    
    def _get_demo_supplier_analytics(self):
        """Get demo supplier analytics"""
        suppliers = self.demo_data.get('suppliers', [])
        products = [p for p in self.demo_data.get('products', []) if p.get('status', 'active') == 'active']
        
        analytics = []
        for sup in suppliers:
            sup_products = [p for p in products if p.get('supplier_id') == sup['id']]
            if sup_products:
                analytics.append({
                    'id': sup['id'],
                    'supplier_name': sup['name'],
                    'product_count': len(sup_products),
                    'total_quantity': sum(p['quantity'] for p in sup_products),
                    'total_value': sum(p['quantity'] * p['cost_price'] for p in sup_products),
                    'avg_cost': sum(p['cost_price'] for p in sup_products) / len(sup_products),
                    'total_shipments': len(sup_products) * 2,  # Demo data
                })
        
        return analytics
    
    # ==================== TOP PRODUCTS ANALYSIS ====================
    
    def get_top_products(self, limit=10, metric='value'):
        """Get top products by specified metric"""
        if self.is_demo:
            return self._get_demo_top_products(limit, metric)
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            if metric == 'value':
                order_by = "p.quantity * p.cost_price DESC"
            elif metric == 'quantity':
                order_by = "p.quantity DESC"
            elif metric == 'profit_margin':
                order_by = "((p.selling_price - p.cost_price) / p.cost_price * 100) DESC"
            else:
                order_by = "p.quantity * p.cost_price DESC"
            
            cursor.execute(f"""
                SELECT 
                    p.id,
                    p.name,
                    p.sku,
                    p.quantity,
                    p.cost_price,
                    p.selling_price,
                    c.name as category_name,
                    (p.quantity * p.cost_price) as total_value,
                    ((p.selling_price - p.cost_price) / NULLIF(p.cost_price, 0) * 100) as profit_margin
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.status = 'active'
                ORDER BY {order_by}
                LIMIT %s
            """, (limit,))
            
            products = cursor.fetchall()
            return products
        finally:
            cursor.close()
    
    def _get_demo_top_products(self, limit, metric):
        """Get demo top products"""
        products = [p for p in self.demo_data.get('products', []) if p.get('status', 'active') == 'active']
        
        for p in products:
            p['total_value'] = p['quantity'] * p['cost_price']
            p['profit_margin'] = ((p['selling_price'] - p['cost_price']) / p['cost_price'] * 100) if p['cost_price'] > 0 else 0
        
        if metric == 'value':
            sorted_products = sorted(products, key=lambda x: x['total_value'], reverse=True)
        elif metric == 'quantity':
            sorted_products = sorted(products, key=lambda x: x['quantity'], reverse=True)
        elif metric == 'profit_margin':
            sorted_products = sorted(products, key=lambda x: x['profit_margin'], reverse=True)
        else:
            sorted_products = sorted(products, key=lambda x: x['total_value'], reverse=True)
        
        return sorted_products[:limit]
    
    # ==================== PROFIT & MARGIN ANALYSIS ====================
    
    def get_profit_analysis(self):
        """Calculate profit and margin analytics"""
        if self.is_demo:
            return self._get_demo_profit_analysis()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    SUM(p.quantity * p.cost_price) as total_cost,
                    SUM(p.quantity * p.selling_price) as total_selling_value,
                    SUM(p.quantity * (p.selling_price - p.cost_price)) as total_profit,
                    AVG((p.selling_price - p.cost_price) / NULLIF(p.cost_price, 0) * 100) as avg_margin_percent
                FROM products p
                WHERE p.status = 'active'
            """)
            
            result = cursor.fetchone()
            
            return {
                'total_cost': float(result['total_cost'] or 0),
                'total_selling_value': float(result['total_selling_value'] or 0),
                'total_profit': float(result['total_profit'] or 0),
                'avg_margin_percent': float(result['avg_margin_percent'] or 0),
                'profit_margin': float(result['total_profit'] or 0) / float(result['total_selling_value'] or 1) * 100
            }
        finally:
            cursor.close()
    
    def _get_demo_profit_analysis(self):
        """Get demo profit analysis"""
        products = [p for p in self.demo_data.get('products', []) if p.get('status', 'active') == 'active']
        
        total_cost = sum(p['quantity'] * p['cost_price'] for p in products)
        total_selling = sum(p['quantity'] * p['selling_price'] for p in products)
        total_profit = total_selling - total_cost
        
        return {
            'total_cost': total_cost,
            'total_selling_value': total_selling,
            'total_profit': total_profit,
            'avg_margin_percent': 25.5,
            'profit_margin': (total_profit / total_selling * 100) if total_selling > 0 else 0
        }
    
    # ==================== ALERTS & WARNINGS ====================
    
    def get_critical_alerts(self):
        """Get critical alerts and warnings"""
        if self.is_demo:
            return self._get_demo_critical_alerts()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.quantity,
                    p.min_stock_level,
                    'low_stock' as alert_type,
                    CONCAT(p.name, ' is running low on stock') as message
                FROM products p
                WHERE p.quantity <= p.min_stock_level AND p.status = 'active'
                
                UNION ALL
                
                SELECT 
                    p.id,
                    p.name,
                    p.quantity,
                    0,
                    'out_of_stock' as alert_type,
                    CONCAT(p.name, ' is out of stock') as message
                FROM products p
                WHERE p.quantity = 0 AND p.status = 'active'
                
                UNION ALL
                
                SELECT 
                    p.id,
                    p.name,
                    0,
                    0,
                    'expiring_soon' as alert_type,
                    CONCAT(p.name, ' expires on ', DATE_FORMAT(p.expiry_date, '%Y-%m-%d')) as message
                FROM products p
                WHERE p.expiry_date IS NOT NULL
                AND p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                AND p.expiry_date >= CURDATE()
                AND p.status = 'active'
                
                ORDER BY alert_type, name
            """)
            
            alerts = cursor.fetchall()
            return alerts
        finally:
            cursor.close()
    
    def _get_demo_critical_alerts(self):
        """Get demo critical alerts"""
        products = self.demo_data.get('products', [])
        alerts = []
        
        for p in products:
            if p.get('status', 'active') == 'active':
                if p['quantity'] == 0:
                    alerts.append({
                        'id': p['id'],
                        'name': p['name'],
                        'quantity': p['quantity'],
                        'alert_type': 'out_of_stock',
                        'message': f"{p['name']} is out of stock"
                    })
                elif p['quantity'] <= p['min_stock_level']:
                    alerts.append({
                        'id': p['id'],
                        'name': p['name'],
                        'quantity': p['quantity'],
                        'alert_type': 'low_stock',
                        'message': f"{p['name']} is running low on stock"
                    })
        
        return alerts
    
    # ==================== DASHBOARD SUMMARY ====================
    
    def get_dashboard_summary(self):
        """Get comprehensive dashboard summary"""
        return {
            'kpis': self.get_kpis(),
            'category_analytics': self.get_category_analytics(),
            'supplier_analytics': self.get_supplier_analytics(),
            'top_products': self.get_top_products(limit=5),
            'critical_alerts': self.get_critical_alerts(),
            'profit_analysis': self.get_profit_analysis(),
        }
