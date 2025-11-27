#!/usr/bin/env python3
"""
Payroll service for database operations
"""

from .models import Payroll, get_db_connection, DB_PATH
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class PayrollService:
    """Service for managing payroll calculations in the database"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
    
    def create_payroll(self, payroll: Payroll) -> int:
        """Create a new payroll entry and return its ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO payroll 
                (employee_id, employee_name, order_id, order_date, order_value,
                 payment_percent, calculated_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payroll.employee_id,
                payroll.employee_name,
                payroll.order_id,
                payroll.order_date,
                payroll.order_value,
                payroll.payment_percent,
                payroll.calculated_amount,
                payroll.created_at
            ))
            
            payroll_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created payroll entry with ID: {payroll_id}")
            return payroll_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating payroll: {e}")
            raise
        finally:
            conn.close()
    
    def get_payroll_by_employee_id(self, employee_id: int, limit: Optional[int] = None, 
                                   offset: Optional[int] = None) -> List[Payroll]:
        """Get all payroll entries for a specific employee"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM payroll WHERE employee_id = ? ORDER BY created_at DESC'
            if limit is not None:
                query += f' LIMIT {limit}'
                if offset is not None:
                    query += f' OFFSET {offset}'
            
            cursor.execute(query, (employee_id,))
            rows = cursor.fetchall()
            
            payroll_entries = []
            for row in rows:
                payroll_entries.append(Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    created_at=row['created_at']
                ))
            return payroll_entries
        finally:
            conn.close()
    
    def get_all_payroll(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Payroll]:
        """Get all payroll entries sorted by created_at DESC"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM payroll ORDER BY created_at DESC'
            if limit is not None:
                query += f' LIMIT {limit}'
                if offset is not None:
                    query += f' OFFSET {offset}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            payroll_entries = []
            for row in rows:
                payroll_entries.append(Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    created_at=row['created_at']
                ))
            return payroll_entries
        finally:
            conn.close()
    
    def get_payroll_summary_by_employee(self) -> List[dict]:
        """Get payroll summary grouped by employee with total amounts"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    employee_id,
                    employee_name,
                    COUNT(*) as order_count,
                    SUM(calculated_amount) as total_amount,
                    MIN(order_date) as first_order_date,
                    MAX(order_date) as last_order_date
                FROM payroll
                GROUP BY employee_id, employee_name
                ORDER BY total_amount DESC
            ''')
            rows = cursor.fetchall()
            
            summary = []
            for row in rows:
                summary.append({
                    'employee_id': row['employee_id'],
                    'employee_name': row['employee_name'],
                    'order_count': row['order_count'],
                    'total_amount': row['total_amount'],
                    'first_order_date': row['first_order_date'],
                    'last_order_date': row['last_order_date']
                })
            return summary
        finally:
            conn.close()
    
    def get_payroll_count_by_employee(self, employee_id: int) -> int:
        """Get total count of payroll entries for an employee"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) as count FROM payroll WHERE employee_id = ?', (employee_id,))
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def get_total_payroll_amount_by_employee(self, employee_id: int) -> float:
        """Get total payroll amount for an employee"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT SUM(calculated_amount) as total FROM payroll WHERE employee_id = ?', (employee_id,))
            row = cursor.fetchone()
            return row['total'] if row and row['total'] else 0.0
        finally:
            conn.close()

