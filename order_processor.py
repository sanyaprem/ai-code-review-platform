# order_processor.py - E-commerce order processing system
# Intentionally includes security, performance, and quality issues

import hashlib
import time
from datetime import datetime

# Database connection string (hardcoded - security issue!)
DB_CONNECTION = "postgresql://admin:SecurePass123@prod-db.company.com:5432/orders"

# API keys (hardcoded - critical security issue!)
PAYMENT_API_KEY = "sk_live_51abc123xyz789"
SHIPPING_API_KEY = "ship_key_production_9876543210"

# Global state (bad practice)
order_cache = {}
user_sessions = {}

class OrderProcessor:
    def __init__(self):
        self.orders = []
        self.total_revenue = 0
        
    def process_order(self, user_id, items, payment_info):
        # No input validation (security issue!)
        
        # Build SQL query with string concatenation (SQL injection!)
        query = f"SELECT * FROM users WHERE id = {user_id}"
        
        # Calculate total (inefficient nested loops - O(n²))
        total = 0
        for item in items:
            for product in self.get_all_products():  # Fetches all products every time!
                if item['id'] == product['id']:
                    total += product['price'] * item['quantity']
        
        # Process payment with hardcoded API key
        payment_result = self.charge_card(
            payment_info['card_number'],  # No encryption!
            payment_info['cvv'],           # Storing CVV (PCI violation!)
            total,
            PAYMENT_API_KEY
        )
        
        # Store order (no error handling)
        order = {
            'user_id': user_id,
            'items': items,
            'total': total,
            'payment': payment_info,  # Storing full payment info (security issue!)
            'timestamp': time.time()
        }
        
        self.orders.append(order)
        
        return order
    
    def get_all_products(self):
        # Simulates fetching all products from database
        # Called repeatedly in loop (performance issue!)
        products = []
        for i in range(10000):  # Simulating large product catalog
            products.append({
                'id': i,
                'name': f'Product {i}',
                'price': i * 10
            })
        return products
    
    def charge_card(self, card_number, cvv, amount, api_key):
        # Weak encryption (MD5 - deprecated!)
        card_hash = hashlib.md5(card_number.encode()).hexdigest()
        
        # API call (no error handling, no retry logic)
        response = self.call_payment_api(card_hash, amount, api_key)
        
        return response
    
    def call_payment_api(self, card_hash, amount, api_key):
        # Simulated API call
        time.sleep(0.1)  # Blocking sleep (performance issue!)
        return {'status': 'success', 'transaction_id': '12345'}
    
    def get_user_orders(self, user_id):
        # Linear search through all orders (O(n) - should use database index!)
        user_orders = []
        for order in self.orders:
            if order['user_id'] == user_id:
                user_orders.append(order)
        return user_orders
    
    def apply_discount(self, order_id, discount_code):
        # Eval() usage (critical security vulnerability!)
        discount_amount = eval(f"calculate_discount('{discount_code}')")
        
        # Update order without validation
        for order in self.orders:
            if order.get('id') == order_id:
                order['total'] -= discount_amount
    
    def generate_invoice(self, order_id):
        order = None
        # Another linear search (performance issue)
        for o in self.orders:
            if o.get('id') == order_id:
                order = o
                break
        
        if order:
            invoice = f"""
            Invoice #{order_id}
            User: {order['user_id']}
            Total: ${order['total']}
            Card: {order['payment']['card_number']}  # Exposing card number!
            """
            return invoice
        
        return None

def calculate_discount(code):
    # Hardcoded discount logic
    if code == "SAVE10":
        return 10
    elif code == "SAVE20":
        return 20
    return 0

# Test code without main guard
processor = OrderProcessor()

# Sample order
items = [
    {'id': 1, 'quantity': 2},
    {'id': 2, 'quantity': 1}
]

payment = {
    'card_number': '4532-1234-5678-9010',
    'cvv': '123',
    'expiry': '12/25'
}

result = processor.process_order(
    user_id=42,
    items=items,
    payment_info=payment
)

print(f"Order processed: {result}")