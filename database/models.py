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
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

