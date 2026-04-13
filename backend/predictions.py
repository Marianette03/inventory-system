"""
Predictive Analytics Module for Inventory System
Provides trend analysis, forecasting, and predictions
"""

from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import math

class PredictiveAnalytics:
    """Advanced predictive analytics for inventory forecasting"""
    
    def __init__(self, db_connection=None, demo_data=None):
        self.db = db_connection
        self.demo_data = demo_data
        self.is_demo = demo_data is not None
    
    # ==================== DEMAND FORECASTING ====================
    
    def forecast_demand(self, product_id, days_ahead=30):
        """Forecast demand for a product using simple moving average"""
        if self.is_demo:
            return self._demo_forecast_demand(product_id, days_ahead)
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get historical movements for the product (last 90 days)
            cursor.execute("""
                SELECT DATE(created_at) as date, SUM(ABS(quantity)) as quantity
                FROM stock_movements
                WHERE product_id = %s AND movement_type = 'out'
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (product_id,))
            
            movements = cursor.fetchall()
            
            if not movements:
                return {
                    'product_id': product_id,
                    'forecast': [{'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'), 
                                 'predicted_demand': 0} for i in range(days_ahead)],
                    'confidence': 0,
                    'trend': 'flat',
                    'message': 'Insufficient data for prediction'
                }
            
            # Calculate moving average (14-day window)
            quantities = [m['quantity'] for m in movements[-14:]]
            avg_demand = statistics.mean(quantities) if quantities else 0
            
            # Calculate trend
            first_half = statistics.mean([m['quantity'] for m in movements[:len(movements)//2]]) if len(movements) > 7 else avg_demand
            second_half = statistics.mean([m['quantity'] for m in movements[len(movements)//2:]]) if len(movements) > 7 else avg_demand
            
            trend_percentage = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
            
            if trend_percentage > 5:
                trend = 'increasing'
                trend_factor = 1.05
            elif trend_percentage < -5:
                trend = 'decreasing'
                trend_factor = 0.95
            else:
                trend = 'stable'
                trend_factor = 1.0
            
            # Generate forecast
            forecast = []
            current_demand = avg_demand
            
            for i in range(days_ahead):
                forecast_date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                # Add some randomness but keep it within bounds
                current_demand = max(0, current_demand * trend_factor + self._noise(-2, 2))
                forecast.append({
                    'date': forecast_date,
                    'predicted_demand': round(current_demand, 2)
                })
            
            # Calculate confidence based on consistency of historical data
            if len(quantities) > 1:
                std_dev = statistics.stdev(quantities)
                coefficient_of_variation = (std_dev / avg_demand * 100) if avg_demand > 0 else 0
                confidence = max(0, 100 - coefficient_of_variation)
            else:
                confidence = 50
            
            return {
                'product_id': product_id,
                'forecast': forecast,
                'confidence': round(confidence, 2),
                'trend': trend,
                'avg_daily_demand': round(avg_demand, 2),
                'message': f'Forecast based on {len(movements)} days of data'
            }
        finally:
            cursor.close()
    
    def _demo_forecast_demand(self, product_id, days_ahead):
        """Demo forecast demand"""
        products = self.demo_data.get('products', [])
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return None
        
        # Demo forecast data
        avg_demand = 5 + (product['quantity'] * 0.1)
        forecast = []
        
        for i in range(days_ahead):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            # Simple trend: gradually decreasing demand
            predicted = max(0, avg_demand * (1 - (i * 0.002)))
            forecast.append({
                'date': date,
                'predicted_demand': round(predicted, 2)
            })
        
        return {
            'product_id': product_id,
            'forecast': forecast,
            'confidence': 75.5,
            'trend': 'stable',
            'avg_daily_demand': round(avg_demand, 2),
            'message': 'Demo forecast data'
        }
    
    # ==================== REORDER POINT CALCULATION ====================
    
    def calculate_reorder_point(self, product_id):
        """
        Calculate optimal reorder point using:
        ROP = (Average Daily Demand × Lead Time) + Safety Stock
        """
        if self.is_demo:
            return self._demo_reorder_point(product_id)
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get product info
            cursor.execute("""
                SELECT quantity, min_stock_level, max_stock_level, cost_price
                FROM products WHERE id = %s
            """, (product_id,))
            
            product = cursor.fetchone()
            if not product:
                return None
            
            # Get average daily demand (last 30 days)
            cursor.execute("""
                SELECT COALESCE(AVG(daily_qty), 0) as avg_demand
                FROM (
                    SELECT DATE(created_at) as date, SUM(ABS(quantity)) as daily_qty
                    FROM stock_movements
                    WHERE product_id = %s AND movement_type = 'out'
                    AND created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                ) as daily_data
            """, (product_id,))
            
            result = cursor.fetchone()
            avg_daily_demand = result['avg_demand'] if result else 0
            
            # Assumed lead time (3 days)
            lead_time_days = 3
            
            # Calculate safety stock (1 week buffer)
            safety_stock = avg_daily_demand * 7
            
            # Calculate ROP
            reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
            
            # Calculate EOQ (Economic Order Quantity)
            holding_cost = product['cost_price'] * 0.25  # 25% of cost
            ordering_cost = 100  # Fixed ordering cost
            
            if holding_cost > 0:
                eoq = math.sqrt((2 * avg_daily_demand * 365 * ordering_cost) / holding_cost)
            else:
                eoq = 0
            
            return {
                'product_id': product_id,
                'avg_daily_demand': round(avg_daily_demand, 2),
                'lead_time_days': lead_time_days,
                'safety_stock': round(safety_stock, 2),
                'reorder_point': round(reorder_point, 2),
                'eoq': round(eoq, 0),
                'current_quantity': product['quantity'],
                'recommendation': 'REORDER' if product['quantity'] <= reorder_point else 'SUFFICIENT'
            }
        finally:
            cursor.close()
    
    def _demo_reorder_point(self, product_id):
        """Demo reorder point calculation"""
        products = self.demo_data.get('products', [])
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return None
        
        avg_daily_demand = product['quantity'] * 0.05
        lead_time = 3
        safety_stock = avg_daily_demand * 7
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        
        return {
            'product_id': product_id,
            'avg_daily_demand': round(avg_daily_demand, 2),
            'lead_time_days': lead_time,
            'safety_stock': round(safety_stock, 2),
            'reorder_point': round(reorder_point, 2),
            'eoq': round(product['quantity'] * 1.5, 0),
            'current_quantity': product['quantity'],
            'recommendation': 'REORDER' if product['quantity'] <= reorder_point else 'SUFFICIENT'
        }
    
    # ==================== STOCK IN TREND ANALYSIS ====================
    
    def analyze_stock_in_trend(self):
        """Analyze stock inflow trends"""
        if self.is_demo:
            return self._demo_stock_in_trend()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    WEEK(created_at) as week,
                    YEAR(created_at) as year,
                    SUM(quantity) as total_in,
                    COUNT(*) as transaction_count,
                    AVG(quantity) as avg_transaction
                FROM stock_movements
                WHERE movement_type = 'in'
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 12 WEEK)
                GROUP BY YEAR(created_at), WEEK(created_at)
                ORDER BY year, week
            """)
            
            trends = cursor.fetchall()
            
            if trends:
                avg_in = statistics.mean([t['total_in'] for t in trends])
                recent_avg = statistics.mean([t['total_in'] for t in trends[-4:]])
                trend = 'increasing' if recent_avg > avg_in else 'decreasing' if recent_avg < avg_in else 'stable'
            else:
                trend = 'no_data'
            
            return {
                'weekly_trends': trends,
                'trend': trend,
                'average_weekly_in': round(avg_in, 2) if trends else 0,
                'total_transactions': sum(t['transaction_count'] for t in trends) if trends else 0
            }
        finally:
            cursor.close()
    
    def _demo_stock_in_trend(self):
        """Demo stock in trend"""
        weeks = []
        base_qty = 150
        
        for i in range(12):
            weeks.append({
                'week': datetime.now().isocalendar()[1] - i,
                'year': datetime.now().year,
                'total_in': base_qty - (i * 5),
                'transaction_count': 3 + i % 5,
                'avg_transaction': 25 + (i * 2)
            })
        
        return {
            'weekly_trends': weeks[::-1],
            'trend': 'stable',
            'average_weekly_in': 150,
            'total_transactions': 45
        }
    
    # ==================== WASTAGE & EXPIRY PREDICTION ====================
    
    def predict_expiry_impact(self):
        """Predict impact of expiring products"""
        if self.is_demo:
            return self._demo_expiry_impact()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.quantity,
                    p.cost_price,
                    p.expiry_date,
                    DATEDIFF(p.expiry_date, CURDATE()) as days_until_expiry,
                    (p.quantity * p.cost_price) as potential_loss
                FROM products p
                WHERE p.expiry_date IS NOT NULL
                AND p.expiry_date >= CURDATE()
                AND p.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 90 DAY)
                AND p.status = 'active'
                ORDER BY p.expiry_date ASC
            """)
            
            expiring_products = cursor.fetchall()
            
            # Convert Decimal to float
            for product in expiring_products:
                product['potential_loss'] = float(product['potential_loss'] or 0)
                product['cost_price'] = float(product['cost_price'])
            
            total_potential_loss = sum(p['potential_loss'] for p in expiring_products)
            
            # Segment by urgency
            critical = [p for p in expiring_products if p['days_until_expiry'] <= 7]
            warning = [p for p in expiring_products if 7 < p['days_until_expiry'] <= 30]
            monitor = [p for p in expiring_products if 30 < p['days_until_expiry'] <= 90]
            
            return {
                'total_expiring_products': len(expiring_products),
                'total_potential_loss': round(total_potential_loss, 2),
                'critical_count': len(critical),  # Expires in 7 days
                'warning_count': len(warning),     # Expires in 8-30 days
                'monitor_count': len(monitor),     # Expires in 31-90 days
                'products': {
                    'critical': critical,
                    'warning': warning,
                    'monitor': monitor
                }
            }
        finally:
            cursor.close()
    
    def _demo_expiry_impact(self):
        """Demo expiry impact"""
        return {
            'total_expiring_products': 0,
            'total_potential_loss': 0.0,
            'critical_count': 0,
            'warning_count': 0,
            'monitor_count': 0,
            'products': {
                'critical': [],
                'warning': [],
                'monitor': []
            }
        }
    
    # ==================== SEASONAL PATTERNS ====================
    
    def analyze_seasonal_patterns(self, product_id=None):
        """Analyze seasonal shopping patterns"""
        if self.is_demo:
            return self._demo_seasonal_patterns()
        
        cursor = self.db.cursor(dictionary=True)
        
        try:
            if product_id:
                cursor.execute("""
                    SELECT 
                        MONTH(created_at) as month,
                        QUARTER(created_at) as quarter,
                        SUM(ABS(quantity)) as total_quantity,
                        COUNT(*) as transaction_count,
                        AVG(ABS(quantity)) as avg_transaction
                    FROM stock_movements
                    WHERE product_id = %s
                    AND created_at >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                    GROUP BY MONTH(created_at), QUARTER(created_at)
                    ORDER BY month
                """, (product_id,))
            else:
                cursor.execute("""
                    SELECT 
                        MONTH(created_at) as month,
                        QUARTER(created_at) as quarter,
                        SUM(ABS(quantity)) as total_quantity,
                        COUNT(*) as transaction_count,
                        AVG(ABS(quantity)) as avg_transaction
                    FROM stock_movements
                    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                    GROUP BY MONTH(created_at), QUARTER(created_at)
                    ORDER BY month
                """)
            
            patterns = cursor.fetchall()
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            return {
                'monthly_patterns': [{
                    'month': month_names[p['month']-1] if p['month'] else 'Unknown',
                    'quantity': float(p['total_quantity'] or 0),
                    'transactions': p['transaction_count'],
                    'avg_transaction': float(p['avg_transaction'] or 0)
                } for p in patterns],
                'peak_season': 'Q' + str(max([p['quarter'] for p in patterns], default=1)) if patterns else 'N/A',
                'low_season': 'Q' + str(min([p['quarter'] for p in patterns], default=1)) if patterns else 'N/A'
            }
        finally:
            cursor.close()
    
    def _demo_seasonal_patterns(self):
        """Demo seasonal patterns"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        patterns = []
        
        for i, month in enumerate(months):
            # Create a wave pattern
            qty = 100 + 50 * math.sin(i * (math.pi / 6))
            patterns.append({
                'month': month,
                'quantity': qty,
                'transactions': 5 + (i % 3),
                'avg_transaction': 20
            })
        
        return {
            'monthly_patterns': patterns,
            'peak_season': 'Q3',
            'low_season': 'Q1'
        }
    
    # ==================== HELPER FUNCTIONS ====================
    
    def _noise(self, min_val, max_val):
        """Generate low noise for forecasting"""
        import random
        return random.uniform(min_val, max_val)
    
    def get_all_predictions(self):
        """Get comprehensive prediction report"""
        return {
            'stock_in_trends': self.analyze_stock_in_trend(),
            'expiry_predictions': self.predict_expiry_impact(),
            'seasonal_patterns': self.analyze_seasonal_patterns(),
        }
