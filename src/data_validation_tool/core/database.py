from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from .config import (
    MONGODB_URI, DATABASE_NAME,
    MONGODB_CONNECT_TIMEOUT_MS,
    MONGODB_SERVER_SELECTION_TIMEOUT_MS,
    MONGODB_MAX_POOL_SIZE,
    MONGODB_MIN_POOL_SIZE,
    MONGODB_MAX_IDLE_TIME_MS
)

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """MongoDB 数据库连接管理"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        """连接到 MongoDB"""
        try:
            self.client = MongoClient(
                MONGODB_URI,
                connectTimeoutMS=MONGODB_CONNECT_TIMEOUT_MS,
                serverSelectionTimeoutMS=MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                maxPoolSize=MONGODB_MAX_POOL_SIZE,
                minPoolSize=MONGODB_MIN_POOL_SIZE,
                maxIdleTimeMS=MONGODB_MAX_IDLE_TIME_MS
            )
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            logger.info(f"成功连接到 MongoDB 数据库: {DATABASE_NAME}")
            return True
        except ConnectionFailure as e:
            logger.error(f"MongoDB 连接失败: {e}")
            return False
        except Exception as e:
            logger.error(f"连接异常: {e}")
            return False

    def get_database(self):
        """获取数据库实例"""
        if self.db is None:
            self.connect()
        return self.db

    def get_collection(self, collection_name):
        """获取指定的集合"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 连接已关闭")


def get_db_connection():
    """获取数据库连接单例"""
    return DatabaseConnection()
