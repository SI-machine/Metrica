#!/usr/bin/env python3
"""
Employee service for database operations
"""

from .models import Employee, get_db_connection, DB_PATH
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class EmployeeService:
    """Service for managing employees in the database"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
    
    def create_employee(self, employee: Employee) -> int:
        """Create a new employee and return its ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees 
                (employee_name, phone_number, payment_method, payment_value,
                 date_started, email, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee.employee_name,
                employee.phone_number,
                employee.payment_method,
                employee.payment_value,
                employee.date_started,
                employee.email,
                employee.status,
                employee.notes,
                employee.created_at
            ))
            
            employee_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created employee with ID: {employee_id}")
            return employee_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating employee: {e}")
            raise
        finally:
            conn.close()
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,))
            row = cursor.fetchone()
            
            if row:
                return Employee(
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    phone_number=row['phone_number'],
                    payment_method=row['payment_method'],
                    payment_value=row['payment_value'],
                    date_started=row['date_started'],
                    email=row['email'],
                    status=row['status'],
                    notes=row['notes'],
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def get_employee_by_name(self, employee_name: str) -> Optional[Employee]:
        """Get employee by name"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM employees WHERE employee_name = ?', (employee_name,))
            row = cursor.fetchone()
            
            if row:
                return Employee(
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    phone_number=row['phone_number'],
                    payment_method=row['payment_method'],
                    payment_value=row['payment_value'],
                    date_started=row['date_started'],
                    email=row['email'],
                    status=row['status'],
                    notes=row['notes'],
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def get_all_employees(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Employee]:
        """Get all employees sorted by created_at DESC (most recent first)"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM employees ORDER BY created_at DESC'
            if limit is not None:
                query += f' LIMIT {limit}'
                if offset is not None:
                    query += f' OFFSET {offset}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            employees = []
            for row in rows:
                employees.append(Employee(
                    employee_id=row['employee_id'],
                    employee_name=row['employee_name'],
                    phone_number=row['phone_number'],
                    payment_method=row['payment_method'],
                    payment_value=row['payment_value'],
                    date_started=row['date_started'],
                    email=row['email'],
                    status=row['status'],
                    notes=row['notes'],
                    created_at=row['created_at']
                ))
            return employees
        finally:
            conn.close()
    
    def get_employees_count(self) -> int:
        """Get total count of employees"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) as count FROM employees')
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def update_employee(self, employee: Employee) -> bool:
        """Update an existing employee"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            from datetime import datetime
            cursor.execute('''
                UPDATE employees 
                SET employee_name = ?, phone_number = ?, payment_method = ?,
                    payment_value = ?, date_started = ?, email = ?,
                    status = ?, notes = ?, updated_at = ?
                WHERE employee_id = ?
            ''', (
                employee.employee_name,
                employee.phone_number,
                employee.payment_method,
                employee.payment_value,
                employee.date_started,
                employee.email,
                employee.status,
                employee.notes,
                datetime.now().isoformat(),
                employee.employee_id
            ))
            
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Updated employee with ID: {employee.employee_id}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating employee: {e}")
            raise
        finally:
            conn.close()
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM employees WHERE employee_id = ?', (employee_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Deleted employee with ID: {employee_id}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting employee: {e}")
            raise
        finally:
            conn.close()

