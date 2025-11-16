#!/usr/bin/env python3
"""
Order service for database operations
"""

from .models import Order, get_db_connection, DB_PATH
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class OrderService:
    """Service for managing orders in the database"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
    
    def create_order(self, order: Order) -> int:
        """Create a new order and return its ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO orders 
                (client_name, description, date, employee_name, income_value, 
                 status, client_contact, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.client_name,
                order.description,
                order.date,
                order.employee_name,
                order.income_value,
                order.status,
                order.client_contact,
                order.created_at
            ))
            
            order_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created order with ID: {order_id}")
            return order_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating order: {e}")
            raise
        finally:
            conn.close()
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
            row = cursor.fetchone()
            
            if row:
                return Order(
                    order_id=row['order_id'],
                    client_name=row['client_name'],
                    description=row['description'],
                    date=row['date'],
                    employee_name=row['employee_name'],
                    income_value=row['income_value'],
                    status=row['status'],
                    client_contact=row['client_contact'],
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def get_orders_by_date(self, date: str) -> List[Order]:
        """Get all orders for a specific date"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM orders WHERE date = ? ORDER BY created_at DESC', (date,))
            rows = cursor.fetchall()
            
            orders = []
            for row in rows:
                orders.append(Order(
                    order_id=row['order_id'],
                    client_name=row['client_name'],
                    description=row['description'],
                    date=row['date'],
                    employee_name=row['employee_name'],
                    income_value=row['income_value'],
                    status=row['status'],
                    client_contact=row['client_contact'],
                    created_at=row['created_at']
                ))
            return orders
        finally:
            conn.close()
    
    def update_order(self, order: Order) -> bool:
        """Update an existing order"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            from datetime import datetime
            cursor.execute('''
                UPDATE orders 
                SET client_name = ?, description = ?, date = ?, 
                    employee_name = ?, income_value = ?, status = ?,
                    client_contact = ?, updated_at = ?
                WHERE order_id = ?
            ''', (
                order.client_name,
                order.description,
                order.date,
                order.employee_name,
                order.income_value,
                order.status,
                order.client_contact,
                datetime.now().isoformat(),
                order.order_id
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Updated order with ID: {order.order_id}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating order: {e}")
            raise
        finally:
            conn.close()
    
    def delete_order(self, order_id: int) -> bool:
        """Delete an order by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Deleted order with ID: {order_id}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting order: {e}")
            raise
        finally:
            conn.close()

