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
            
            # 创建webhook数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS post_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    result TEXT,
                    timestamp TEXT,
                    screenshot TEXT,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT
                )
            ''')
            
            # 为webhook数据表创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_data_event ON post_data (event)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_data_create_time ON post_data (create_time)')
            
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
    
    def get_duration_data(self, exclude_today: bool = True) -> Dict[str, int]:
        """
        获取持续时间数据，返回字典格式（日期->持续时间）
        
        Args:
            exclude_today: 是否排除今天的数据
            
        Returns:
            Dict[str, int]: 日期到持续时间的映射字典
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
                
                # 取消排序，直接返回数据库中的原始顺序
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # 返回字典格式，确保日期和持续时间的一一对应
                return {row[0]: row[1] for row in rows}
        except Exception as e:
            logger.error(f"获取持续时间数据时发生错误: {e}")
            return {}
    
    def get_item_data(self, exclude_today: bool = True) -> Dict[str, Dict[str, List]]:
        """
        获取物品数据，返回字典格式（日期->物品信息）
        
        Args:
            exclude_today: 是否排除今天的数据
            
        Returns:
            Dict[str, Dict[str, List]]: 日期到物品信息的映射字典
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
                
                # 取消排序，直接返回数据库中的原始顺序
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # 按日期分组返回字典格式
                result = {}
                for row in rows:
                    name, timestamp, date_str, config_group = row
                    if date_str not in result:
                        result[date_str] = {
                            '物品名称': [],
                            '时间': [],
                            '归属配置组': []
                        }
                    result[date_str]['物品名称'].append(name)
                    result[date_str]['时间'].append(timestamp)
                    result[date_str]['归属配置组'].append(config_group or '')
                
                return result
        except Exception as e:
            logger.error(f"获取物品数据时发生错误: {e}")
            return {}
    
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
    
    def save_webhook_data(self, data_dict: Dict) -> bool:
        """
        保存webhook数据到数据库
        
        Args:
            data_dict: 包含webhook数据的字典，必须包含'event'字段
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 可能存在的字段
            possible_fields = ['result', 'timestamp', 'message', 'screenshot']
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建插入语句
                fields = ['event']
                values = [data_dict['event']]
                placeholders = ['?']
                
                # 添加可选字段
                for field in possible_fields:
                    if field in data_dict:
                        fields.append(field)
                        values.append(data_dict[field])
                        placeholders.append('?')
                
                # 执行插入
                query = f'''
                    INSERT INTO post_data ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                '''
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"成功保存webhook数据，事件: {data_dict['event']}")
                return True
                
        except Exception as e:
            logger.error(f"保存webhook数据时发生错误: {e}")
            return False
    
    def cleanup_old_webhook_data(self, days_to_keep: int = 3) -> bool:
        """
        清理指定天数之前的webhook数据
        
        Args:
            days_to_keep: 保留的天数，默认为3天
            
        Returns:
            bool: 操作是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 计算截止日期（当前时间减去指定天数）
                from datetime import timedelta
                cutoff_datetime = datetime.now() - timedelta(days=days_to_keep)
                cutoff_str = cutoff_datetime.strftime('%Y-%m-%d %H:%M:%S')
                
                # 删除指定日期之前的数据
                cursor.execute('''
                    DELETE FROM post_data 
                    WHERE create_time < ?
                ''', (cutoff_str,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"成功清理了 {deleted_count} 条 {days_to_keep} 天前的webhook数据")
                
                return True
                
        except Exception as e:
            logger.error(f"清理旧webhook数据时发生错误: {e}")
            return False

    def get_webhook_data(self, limit: int = 100) -> List[Dict]:
        """
        获取webhook数据列表
        在获取数据前会自动清理三天及更早之前的旧数据
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            List[Dict]: webhook数据列表
        """
        # 在获取数据前先清理旧数据
        self.cleanup_old_webhook_data()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, event, result, timestamp, screenshot, create_time, message
                    FROM post_data
                    ORDER BY create_time DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'event': row[1],
                        'result': row[2],
                        'timestamp': row[3],
                        'screenshot': row[4],
                        'create_time': row[5],
                        'message': row[6]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取webhook数据时发生错误: {e}")
            return []