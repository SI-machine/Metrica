#!/usr/bin/env python3
"""
Income/Expense service for database operations
"""

from .models import IncomeExpense, get_db_connection, DB_PATH
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class IncomeExpenseService:
    """Service for managing income and expense transactions in the database"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
    
    def create_transaction(self, transaction: IncomeExpense) -> int:
        """Create a new income/expense transaction and return its ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO income_expense 
                (transaction_type, value, description, source, order_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                transaction.transaction_type,
                transaction.value,
                transaction.description,
                transaction.source,
                transaction.order_id,
                transaction.created_at
            ))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created {transaction.transaction_type} transaction with ID: {transaction_id}")
            return transaction_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise
        finally:
            conn.close()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[IncomeExpense]:
        """Get transaction by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM income_expense WHERE transaction_id = ?', (transaction_id,))
            row = cursor.fetchone()
            
            if row:
                return IncomeExpense(
                    transaction_id=row['transaction_id'],
                    transaction_type=row['transaction_type'],
                    value=row['value'],
                    description=row['description'],
                    source=row['source'],
                    order_id=row['order_id'],
                    created_at=row['created_at']
                )
            return None
        finally:
            conn.close()
    
    def get_all_transactions(self, transaction_type: Optional[str] = None,
                            limit: Optional[int] = None, offset: Optional[int] = None) -> List[IncomeExpense]:
        """Get all transactions, optionally filtered by type, sorted by created_at DESC"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM income_expense'
            params = []
            
            if transaction_type:
                query += ' WHERE transaction_type = ?'
                params.append(transaction_type)
            
            query += ' ORDER BY created_at DESC'
            
            if limit is not None:
                query += f' LIMIT {limit}'
                if offset is not None:
                    query += f' OFFSET {offset}'
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            transactions = []
            for row in rows:
                transactions.append(IncomeExpense(
                    transaction_id=row['transaction_id'],
                    transaction_type=row['transaction_type'],
                    value=row['value'],
                    description=row['description'],
                    source=row['source'],
                    order_id=row['order_id'],
                    created_at=row['created_at']
                ))
            return transactions
        finally:
            conn.close()
    
    def get_transactions_count(self, transaction_type: Optional[str] = None) -> int:
        """Get total count of transactions, optionally filtered by type"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            if transaction_type:
                cursor.execute('SELECT COUNT(*) as count FROM income_expense WHERE transaction_type = ?', (transaction_type,))
            else:
                cursor.execute('SELECT COUNT(*) as count FROM income_expense')
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
    
    def get_total_income(self) -> float:
        """Get total income amount"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT SUM(value) as total FROM income_expense WHERE transaction_type = ?', ('income',))
            row = cursor.fetchone()
            return row['total'] if row and row['total'] else 0.0
        finally:
            conn.close()
    
    def get_total_expense(self) -> float:
        """Get total expense amount"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT SUM(value) as total FROM income_expense WHERE transaction_type = ?', ('expense',))
            row = cursor.fetchone()
            return row['total'] if row and row['total'] else 0.0
        finally:
            conn.close()
    
    def get_net_profit(self) -> float:
        """Get net profit (total income - total expense)"""
        return self.get_total_income() - self.get_total_expense()
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM income_expense WHERE transaction_id = ?', (transaction_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Deleted transaction with ID: {transaction_id}")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting transaction: {e}")
            raise
        finally:
            conn.close()

