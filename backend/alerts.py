"""
Real-Time Alert Notification System for Inventory Management
Provides instant alerts and notifications for critical events
"""

from datetime import datetime, timedelta
from enum import Enum

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = 'critical'
    WARNING = 'warning'
    INFO = 'info'
    SUCCESS = 'success'

class AlertType(Enum):
    """Types of alerts"""
    LOW_STOCK = 'low_stock'
    OUT_OF_STOCK = 'out_of_stock'
    OVERSTOCK = 'overstock'
    EXPIRING_SOON = 'expiring_soon'
    EXPIRED = 'expired'
    UNUSUAL_ACTIVITY = 'unusual_activity'
    LOW_VALUE = 'low_value'
    HIGH_DEMAND = 'high_demand'

class RealtimeAlertSystem:
    """Real-time alert notification system"""
    
    def __init__(self, db_connection=None, demo_data=None):
        self.db = db_connection
        self.demo_data = demo_data
        self.is_demo = demo_data is not None
    
    # ==================== ALERT GENERATION ====================
    
    def check_stock_levels(self):
        """Check for low and out of stock alerts"""
        if self.is_demo:
            return self._demo_stock_alerts()
        
        cursor = self.db.cursor(dictionary=True)
        alerts = []
        
        try:
            # Check for out of stock
            cursor.execute("""
                SELECT p.id, p.name, p.quantity, s.name as supplier_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.quantity = 0 AND p.status = 'active'
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'out_of_stock' 
                     AND is_read = FALSE) = 0
            """)
            
            out_of_stock = cursor.fetchall()
            for product in out_of_stock:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.OUT_OF_STOCK.value,
                    'severity': AlertSeverity.CRITICAL.value,
                    'title': f"CRITICAL: {product['name']} is out of stock",
                    'message': f"Product {product['name']} has no stock available. Contact {product['supplier_name'] or 'supplier'} immediately.",
                    'action_required': True,
                    'recommended_action': 'Reorder immediately'
                })
            
            # Check for low stock
            cursor.execute("""
                SELECT p.id, p.name, p.quantity, p.min_stock_level, 
                       u.unit_name, s.name as supplier_name
                FROM products p
                LEFT JOIN units u ON p.unit_id = u.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.quantity > 0 AND p.quantity <= p.min_stock_level 
                AND p.status = 'active'
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'low_stock' 
                     AND is_read = FALSE AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)) = 0
            """)
            
            low_stock = cursor.fetchall()
            for product in low_stock:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.LOW_STOCK.value,
                    'severity': AlertSeverity.WARNING.value,
                    'title': f"WARNING: {product['name']} stock is low",
                    'message': f"{product['name']} has {product['quantity']} {product['unit_name']} remaining (minimum: {product['min_stock_level']})",
                    'action_required': True,
                    'recommended_action': f"Consider reordering {product['min_stock_level']} + 20% buffer"
                })
            
            # Check for overstock
            cursor.execute("""
                SELECT p.id, p.name, p.quantity, p.max_stock_level, u.unit_name
                FROM products p
                LEFT JOIN units u ON p.unit_id = u.id
                WHERE p.quantity > p.max_stock_level AND p.status = 'active'
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'overstock' 
                     AND is_read = FALSE) = 0
            """)
            
            overstock = cursor.fetchall()
            for product in overstock:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.OVERSTOCK.value,
                    'severity': AlertSeverity.INFO.value,
                    'title': f"INFO: {product['name']} is overstocked",
                    'message': f"{product['name']} has {product['quantity']} {product['unit_name']}, exceeding max level of {product['max_stock_level']}",
                    'action_required': False,
                    'recommended_action': 'Monitor for potential wastage'
                })
        
        finally:
            cursor.close()
        
        return alerts
    
    def _demo_stock_alerts(self):
        """Generate demo stock alerts"""
        alerts = []
        products = self.demo_data.get('products', [])
        
        for p in products:
            if p['quantity'] == 0:
                alerts.append({
                    'product_id': p['id'],
                    'product_name': p['name'],
                    'alert_type': AlertType.OUT_OF_STOCK.value,
                    'severity': AlertSeverity.CRITICAL.value,
                    'title': f"CRITICAL: {p['name']} is out of stock",
                    'message': f"Product {p['name']} has no stock available.",
                    'action_required': True,
                    'recommended_action': 'Reorder immediately'
                })
            elif p['quantity'] <= p['min_stock_level']:
                alerts.append({
                    'product_id': p['id'],
                    'product_name': p['name'],
                    'alert_type': AlertType.LOW_STOCK.value,
                    'severity': AlertSeverity.WARNING.value,
                    'title': f"WARNING: {p['name']} stock is low",
                    'message': f"{p['name']} has {p['quantity']} units (min: {p['min_stock_level']})",
                    'action_required': True,
                    'recommended_action': 'Consider reordering'
                })
        
        return alerts
    
    # ==================== EXPIRY ALERTS ====================
    
    def check_expiry_alerts(self):
        """Check for expiring and expired products"""
        if self.is_demo:
            return []
        
        cursor = self.db.cursor(dictionary=True)
        alerts = []
        
        try:
            # Check for expired items
            cursor.execute("""
                SELECT p.id, p.name, p.expiry_date, p.quantity, 
                       (p.quantity * p.cost_price) as value_at_risk
                FROM products p
                WHERE p.expiry_date < CURDATE() AND p.status = 'active'
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'expired' 
                     AND is_read = FALSE) = 0
            """)
            
            expired = cursor.fetchall()
            for product in expired:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.EXPIRED.value,
                    'severity': AlertSeverity.CRITICAL.value,
                    'title': f"CRITICAL: {product['name']} has expired",
                    'message': f"{product['name']} expired on {product['expiry_date']}. {product['quantity']} units at risk. Value: ₱{product['value_at_risk']}",
                    'action_required': True,
                    'recommended_action': 'Remove from inventory and dispose',
                    'value_at_risk': float(product['value_at_risk'] or 0)
                })
            
            # Check for expiring soon (within 7 days)
            cursor.execute("""
                SELECT p.id, p.name, p.expiry_date, p.quantity, 
                       DATEDIFF(p.expiry_date, CURDATE()) as days_until_expiry,
                       (p.quantity * p.cost_price) as value_at_risk
                FROM products p
                WHERE p.expiry_date >= CURDATE() 
                AND p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                AND p.status = 'active'
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'expiring_soon' 
                     AND is_read = FALSE AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)) = 0
            """)
            
            expiring_soon = cursor.fetchall()
            for product in expiring_soon:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.EXPIRING_SOON.value,
                    'severity': AlertSeverity.WARNING.value,
                    'title': f"WARNING: {product['name']} expiring soon",
                    'message': f"{product['name']} expires in {product['days_until_expiry']} days. {product['quantity']} units available.",
                    'action_required': True,
                    'recommended_action': f"Prioritize selling or use {product['days_until_expiry']} days before expiration",
                    'value_at_risk': float(product['value_at_risk'] or 0)
                })
        
        finally:
            cursor.close()
        
        return alerts
    
    # ==================== ACTIVITY ALERTS ====================
    
    def check_unusual_activity(self):
        """Check for unusual inventory activity"""
        if self.is_demo:
            return []
        
        cursor = self.db.cursor(dictionary=True)
        alerts = []
        
        try:
            # Check for unusual large movements
            cursor.execute("""
                SELECT sm.id, sm.product_id, p.name, sm.movement_type, sm.quantity, 
                       sm.reason, sm.created_at
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                WHERE sm.created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                AND ABS(sm.quantity) > (SELECT AVG(ABS(quantity)) * 3 
                                       FROM stock_movements 
                                       WHERE product_id = sm.product_id)
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = sm.product_id AND alert_type = 'unusual_activity' 
                     AND is_read = FALSE AND created_at >= DATE_SUB(NOW(), INTERVAL 2 HOUR)) = 0
            """)
            
            unusual = cursor.fetchall()
            for movement in unusual:
                alerts.append({
                    'product_id': movement['product_id'],
                    'product_name': movement['name'],
                    'alert_type': AlertType.UNUSUAL_ACTIVITY.value,
                    'severity': AlertSeverity.INFO.value,
                    'title': f"INFO: Unusual {movement['movement_type']} activity",
                    'message': f"Unusual {movement['movement_type']} movement detected: {movement['quantity']} units of {movement['name']}. Reason: {movement['reason'] or 'Not specified'}",
                    'action_required': False,
                    'recommended_action': 'Verify activity is legitimate'
                })
        
        finally:
            cursor.close()
        
        return alerts
    
    # ==================== DEMAND ALERTS ====================
    
    def check_high_demand_products(self):
        """Identify products with unusually high demand"""
        if self.is_demo:
            return []
        
        cursor = self.db.cursor(dictionary=True)
        alerts = []
        
        try:
            cursor.execute("""
                SELECT p.id, p.name, p.quantity,
                       SUM(ABS(sm.quantity)) as recent_demand,
                       AVG(ABS(sm.quantity)) as avg_demand
                FROM products p
                LEFT JOIN stock_movements sm ON p.id = sm.product_id 
                           AND sm.movement_type = 'out'
                           AND sm.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                WHERE p.status = 'active'
                GROUP BY p.id, p.name, p.quantity
                HAVING recent_demand > avg_demand * 2
                AND (SELECT COUNT(*) FROM inventory_alerts 
                     WHERE product_id = p.id AND alert_type = 'high_demand' 
                     AND is_read = FALSE) = 0
            """)
            
            high_demand = cursor.fetchall()
            for product in high_demand:
                alerts.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'alert_type': AlertType.HIGH_DEMAND.value,
                    'severity': AlertSeverity.INFO.value,
                    'title': f"INFO: High demand detected for {product['name']}",
                    'message': f"{product['name']} has shown high demand recently ({product['recent_demand']} units in 7 days). Current stock: {product['quantity']}",
                    'action_required': False,
                    'recommended_action': 'Consider increasing stock levels'
                })
        
        finally:
            cursor.close()
        
        return alerts
    
    # ==================== COMPREHENSIVE ALERT AGGREGATION ====================
    
    def get_all_alerts(self):
        """Get all active alerts"""
        alerts = []
        
        alerts.extend(self.check_stock_levels())
        alerts.extend(self.check_expiry_alerts())
        alerts.extend(self.check_unusual_activity())
        alerts.extend(self.check_high_demand_products())
        
        # Sort by severity and timestamp
        severity_order = {
            AlertSeverity.CRITICAL.value: 0,
            AlertSeverity.WARNING.value: 1,
            AlertSeverity.INFO.value: 2,
            AlertSeverity.SUCCESS.value: 3
        }
        
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 999))
        
        return alerts
    
    def get_critical_alerts(self):
        """Get only critical alerts"""
        all_alerts = self.get_all_alerts()
        return [a for a in all_alerts if a['severity'] == AlertSeverity.CRITICAL.value]
    
    def get_alert_summary(self):
        """Get summary of alerts by severity"""
        all_alerts = self.get_all_alerts()
        
        summary = {
            'total_alerts': len(all_alerts),
            'critical': len([a for a in all_alerts if a['severity'] == AlertSeverity.CRITICAL.value]),
            'warning': len([a for a in all_alerts if a['severity'] == AlertSeverity.WARNING.value]),
            'info': len([a for a in all_alerts if a['severity'] == AlertSeverity.INFO.value]),
            'action_required_count': len([a for a in all_alerts if a.get('action_required')])
        }
        
        return summary
    
    # ==================== NOTIFICATION HELPERS ====================
    
    def format_notification(self, alert):
        """Format alert for notification display"""
        return {
            'id': f"{alert['product_id']}_{alert['alert_type']}_{datetime.now().timestamp()}",
            'title': alert['title'],
            'message': alert['message'],
            'severity': alert['severity'],
            'type': alert['alert_type'],
            'action_required': alert.get('action_required', False),
            'recommended_action': alert.get('recommended_action'),
            'timestamp': datetime.now().isoformat(),
            'product_id': alert['product_id'],
            'product_name': alert['product_name']
        }
    
    def save_alert_to_db(self, product_id, alert_type, message):
        """Save alert to database"""
        if self.is_demo:
            return
        
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO inventory_alerts (product_id, alert_type, message)
                VALUES (%s, %s, %s)
            """, (product_id, alert_type, message))
            
            self.db.commit()
        except Exception as e:
            print(f"Error saving alert: {e}")
            self.db.rollback()
        finally:
            cursor.close()
