"""
SQLite数据库操作模块
负责日志数据的持久化存储和查询
"""
import sqlite3
import logging
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger('BetterGI初始化')


class DatabaseManager:
    """
    SQLite数据库管理器
    负责数据库的创建、连接和基本操作
    """
    
    def __init__(self, db_path: str):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建日志文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_str TEXT UNIQUE NOT NULL,
                    duration INTEGER NOT NULL DEFAULT 0,
                    item_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建物品数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    config_group TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date_str) REFERENCES log_files (date_str)
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_date ON items (date_str)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_name ON items (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_files_date ON log_files (date_str)')
            
            conn.commit()
            logger.info("数据库表结构初始化完成")
    
    def insert_log_file_data(self, date_str: str, duration: int, items: List[Dict]) -> bool:
        """
        插入或更新日志文件数据
        
        Args:
            date_str: 日期字符串
            duration: 持续时间（秒）
            items: 物品列表，每个物品包含 name, timestamp, config_group
            
        Returns:
            bool: 操作是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 插入或更新日志文件记录
                cursor.execute('''
                    INSERT OR REPLACE INTO log_files (date_str, duration, item_count, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (date_str, duration, len(items)))
                
                # 删除该日期的旧物品记录
                cursor.execute('DELETE FROM items WHERE date_str = ?', (date_str,))
                
                # 插入新的物品记录
                if items:
                    item_data = [
                        (item['name'], item['timestamp'], date_str, item.get('config_group'))
                        for item in items
                    ]
                    cursor.executemany('''
                        INSERT INTO items (name, timestamp, date_str, config_group)
                        VALUES (?, ?, ?, ?)
                    ''', item_data)
                
                conn.commit()
                logger.info(f"成功存储日期 {date_str} 的数据，包含 {len(items)} 个物品")
                return True
                
        except Exception as e:
            logger.error(f"插入日志数据时发生错误: {e}")
            return False
    
    def get_stored_dates(self) -> List[str]:
        """
        获取数据库中已存储的所有日期
        
        Returns:
            List[str]: 日期字符串列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT date_str FROM log_files ORDER BY date_str DESC')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取存储日期时发生错误: {e}")
            return []
    
    def get_duration_data(self, exclude_today: bool = True) -> Dict[str, List]:
        """
        获取持续时间数据
        
        Args:
            exclude_today: 是否排除今天的数据
            
        Returns:
            Dict[str, List]: 包含日期和持续时间的字典
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT date_str, duration FROM log_files'
                params = []
                
                if exclude_today:
                    today = date.today().strftime('%Y%m%d')
                    query += ' WHERE date_str != ?'
                    params.append(today)
                
                query += ' ORDER BY date_str DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return {
                    '日期': [row[0] for row in rows],
                    '持续时间': [row[1] for row in rows]
                }
        except Exception as e:
            logger.error(f"获取持续时间数据时发生错误: {e}")
            return {'日期': [], '持续时间': []}
    
    def get_item_data(self, exclude_today: bool = True) -> Dict[str, List]:
        """
        获取物品数据
        
        Args:
            exclude_today: 是否排除今天的数据
            
        Returns:
            Dict[str, List]: 包含物品信息的字典
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT name, timestamp, date_str, config_group 
                    FROM items
                '''
                params = []
                
                if exclude_today:
                    today = date.today().strftime('%Y%m%d')
                    query += ' WHERE date_str != ?'
                    params.append(today)
                
                query += ' ORDER BY date_str DESC, timestamp DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return {
                    '物品名称': [row[0] for row in rows],
                    '时间': [row[1] for row in rows],
                    '日期': [row[2] for row in rows],
                    '归属配置组': [row[3] or '' for row in rows]
                }
        except Exception as e:
            logger.error(f"获取物品数据时发生错误: {e}")
            return {'物品名称': [], '时间': [], '日期': [], '归属配置组': []}
    
    def get_log_file_info(self, date_str: str) -> Optional[Dict]:
        """
        获取指定日期的日志文件信息
        
        Args:
            date_str: 日期字符串
            
        Returns:
            Optional[Dict]: 日志文件信息，包含 duration 和 item_count
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT duration, item_count, updated_at 
                    FROM log_files 
                    WHERE date_str = ?
                ''', (date_str,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'duration': row[0],
                        'item_count': row[1],
                        'updated_at': row[2]
                    }
                return None
        except Exception as e:
            logger.error(f"获取日志文件信息时发生错误: {e}")
            return None
    
    def delete_log_data(self, date_str: str) -> bool:
        """
        删除指定日期的所有数据
        
        Args:
            date_str: 日期字符串
            
        Returns:
            bool: 操作是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 删除物品记录
                cursor.execute('DELETE FROM items WHERE date_str = ?', (date_str,))
                
                # 删除日志文件记录
                cursor.execute('DELETE FROM log_files WHERE date_str = ?', (date_str,))
                
                conn.commit()
                logger.info(f"成功删除日期 {date_str} 的所有数据")
                return True
                
        except Exception as e:
            logger.error(f"删除日志数据时发生错误: {e}")
            return False