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
                 payment_percent, calculated_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payroll.employee_id,
                payroll.employee_name,
                payroll.order_id,
                payroll.order_date,
                payroll.order_value,
                payroll.payment_percent,
                payroll.calculated_amount,
                payroll.status,
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
                # Handle status field - may not exist in old databases
                try:
                    status = row['status']
                except (KeyError, IndexError):
                    status = 'pending'
                payroll_entries.append(Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    status=status,
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
                # Handle status field - may not exist in old databases
                try:
                    status = row['status']
                except (KeyError, IndexError):
                    status = 'pending'
                payroll_entries.append(Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    status=status,
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
    
    def get_payroll_by_id(self, payroll_id: int) -> Optional[Payroll]:
        """Get payroll by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM payroll WHERE payroll_id = ?', (payroll_id,))
            row = cursor.fetchone()
            
            if row:
                # Handle status field - may not exist in old databases
                try:
                    status = row['status']
                except (KeyError, IndexError):
                    status = 'pending'
                return Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    status=status,
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def update_payroll_status(self, payroll_id: int, status: str) -> bool:
        """Update payroll status"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE payroll 
                SET status = ?
                WHERE payroll_id = ?
            ''', (status, payroll_id))
            
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Updated payroll {payroll_id} status to {status}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating payroll status: {e}")
            raise
        finally:
            conn.close()
    
    def get_payrolls_by_status(self, status: str, limit: Optional[int] = None, 
                              offset: Optional[int] = None) -> List[Payroll]:
        """Get all payroll entries with a specific status"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM payroll WHERE status = ? ORDER BY created_at DESC'
            if limit is not None:
                query += f' LIMIT {limit}'
                if offset is not None:
                    query += f' OFFSET {offset}'
            
            cursor.execute(query, (status,))
            rows = cursor.fetchall()
            
            payroll_entries = []
            for row in rows:
                # Handle status field - may not exist in old databases
                try:
                    status = row['status']
                except (KeyError, IndexError):
                    status = 'pending'
                payroll_entries.append(Payroll(
                    payroll_id=row['payroll_id'],
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    order_id=row['order_id'],
                    order_date=row['order_date'],
                    order_value=row['order_value'],
                    payment_percent=row['payment_percent'],
                    calculated_amount=row['calculated_amount'],
                    status=status,
                    created_at=row['created_at']
                ))
            return payroll_entries
        finally:
            conn.close()
    
    def mark_payroll_as_paid(self, payroll_id: int) -> bool:
        """Mark payroll as paid and create expense entry"""
        from .income_expense_service import IncomeExpenseService
        from .models import IncomeExpense
        
        # Get the payroll first
        payroll = self.get_payroll_by_id(payroll_id)
        if not payroll:
            logger.error(f"Payroll {payroll_id} not found")
            return False
        
        if payroll.status == 'paid':
            logger.warning(f"Payroll {payroll_id} is already marked as paid")
            return False
        
        # Update status to paid
        success = self.update_payroll_status(payroll_id, 'paid')
        if not success:
            return False
        
        # Create expense entry
        try:
            expense = IncomeExpense(
                transaction_type='expense',
                value=payroll.calculated_amount,
                description=f"Payroll payment for {payroll.employee_name} - Order #{payroll.order_id}",
                source='payroll',
                order_id=payroll.order_id
            )
            
            expense_service = IncomeExpenseService(self.db_path)
            expense_id = expense_service.create_transaction(expense)
            logger.info(f"Expense {expense_id} created for payroll {payroll_id} payment of {payroll.calculated_amount}")
            return True
        except Exception as e:
            logger.error(f"Error creating expense for payroll {payroll_id}: {e}")
            # Rollback the status change
            self.update_payroll_status(payroll_id, 'pending')
            return False

