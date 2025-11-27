#!/usr/bin/env python3
"""
Database models for Metrica Bot
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the project root directory (parent of Metrica directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "Metrica" / "orders.db"

class Order:
    """Order model representing a client order"""
    
    def __init__(self, order_id: Optional[int] = None, client_name: str = "", 
                 description: str = "", date: str = "", employee_name: str = "",
                 income_value: float = 0.0, status: str = "pending",
                 client_contact: str = "", created_at: Optional[str] = None):
        self.order_id = order_id
        self.client_name = client_name
        self.description = description
        self.date = date
        self.employee_name = employee_name
        self.income_value = income_value
        self.status = status
        self.client_contact = client_contact
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'client_name': self.client_name,
            'description': self.description,
            'date': self.date,
            'employee_name': self.employee_name,
            'income_value': self.income_value,
            'status': self.status,
            'client_contact': self.client_contact,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        """Create order from dictionary"""
        return cls(
            order_id=data.get('order_id'),
            client_name=data.get('client_name', ''),
            description=data.get('description', ''),
            date=data.get('date', ''),
            employee_name=data.get('employee_name', ''),
            income_value=data.get('income_value', 0.0),
            status=data.get('status', 'pending'),
            client_contact=data.get('client_contact', ''),
            created_at=data.get('created_at')
        )

class Employee:
    """Employee model representing an employee"""
    
    def __init__(self, employee_id: Optional[int] = None, employee_name: str = "",
                 phone_number: str = "", payment_method: str = "fixed",
                 payment_value: Optional[float] = None, date_started: str = "",
                 email: str = "", status: str = "active", notes: str = "",
                 created_at: Optional[str] = None):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.phone_number = phone_number
        self.payment_method = payment_method  # 'owner', 'in_percent', 'fixed'
        self.payment_value = payment_value  # For percent (0-100) or fixed amount
        self.date_started = date_started
        self.email = email
        self.status = status  # 'active', 'inactive'
        self.notes = notes
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert employee to dictionary"""
        return {
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'phone_number': self.phone_number,
            'payment_method': self.payment_method,
            'payment_value': self.payment_value,
            'date_started': self.date_started,
            'email': self.email,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        """Create employee from dictionary"""
        return cls(
            employee_id=data.get('employee_id'),
            employee_name=data.get('employee_name', ''),
            phone_number=data.get('phone_number', ''),
            payment_method=data.get('payment_method', 'fixed'),
            payment_value=data.get('payment_value'),
            date_started=data.get('date_started', ''),
            email=data.get('email', ''),
            status=data.get('status', 'active'),
            notes=data.get('notes', ''),
            created_at=data.get('created_at')
        )

class Payroll:
    """Payroll model representing payroll calculations for employees"""
    
    def __init__(self, payroll_id: Optional[int] = None, employee_id: int = 0,
                 employee_name: str = "", order_id: int = 0, order_date: str = "",
                 order_value: float = 0.0, payment_percent: Optional[float] = None,
                 calculated_amount: float = 0.0, created_at: Optional[str] = None):
        self.payroll_id = payroll_id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.order_id = order_id
        self.order_date = order_date
        self.order_value = order_value
        self.payment_percent = payment_percent
        self.calculated_amount = calculated_amount
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert payroll to dictionary"""
        return {
            'payroll_id': self.payroll_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'order_id': self.order_id,
            'order_date': self.order_date,
            'order_value': self.order_value,
            'payment_percent': self.payment_percent,
            'calculated_amount': self.calculated_amount,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Payroll':
        """Create payroll from dictionary"""
        return cls(
            payroll_id=data.get('payroll_id'),
            employee_id=data.get('employee_id', 0),
            employee_name=data.get('employee_name', ''),
            order_id=data.get('order_id', 0),
            order_date=data.get('order_date', ''),
            order_value=data.get('order_value', 0.0),
            payment_percent=data.get('payment_percent'),
            calculated_amount=data.get('calculated_amount', 0.0),
            created_at=data.get('created_at')
        )

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get database connection"""
    if db_path is None:
        db_path = str(DB_PATH)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database with orders table"""
    if db_path is None:
        db_path = str(DB_PATH)
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            income_value REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            client_contact TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            phone_number TEXT,
            payment_method TEXT NOT NULL DEFAULT 'fixed',
            payment_value REAL,
            date_started TEXT NOT NULL,
            email TEXT,
            status TEXT DEFAULT 'active',
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            employee_name TEXT NOT NULL,
            order_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            order_value REAL NOT NULL,
            payment_percent REAL,
            calculated_amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

