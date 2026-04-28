import os
from dotenv import load_dotenv

# 加载 .env 文件 - 从config目录
config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
env_file = os.path.join(config_dir, '.env')
load_dotenv(env_file)

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'sit').lower()

# MongoDB 连接配置 - 根据环境选择
if ENVIRONMENT == 'qa':
    MONGODB_URI = os.getenv(
        'MONGODB_URI_QA',
        'mongodb+srv://rs-ghnwuip-qa-rw:ghnw-uip-qa@rs-ghnwuip-qa-pl-0.mirrfq.mongodb.net/qa?retryWrites=true&w=majority'
    )
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'qa')
else:  # 默认sit环境
    MONGODB_URI = os.getenv(
        'MONGODB_URI_SIT',
        'mongodb+srv://rs-ghnwuip-dev-rw:dAjf58MEpHWxFpCA@rs-ghnwuip-dev-pl-0.9gvg0.mongodb.net/sit?retryWrites=true&w=majority'
    )
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'sit')

# MongoDB 连接参数
MONGODB_CONNECT_TIMEOUT_MS = int(os.getenv('MONGODB_CONNECT_TIMEOUT_MS', '30000'))  # 30秒
MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT_MS', '30000'))  # 30秒
MONGODB_MAX_POOL_SIZE = int(os.getenv('MONGODB_MAX_POOL_SIZE', '10'))
MONGODB_MIN_POOL_SIZE = int(os.getenv('MONGODB_MIN_POOL_SIZE', '2'))
MONGODB_MAX_IDLE_TIME_MS = int(os.getenv('MONGODB_MAX_IDLE_TIME_MS', '30000'))  # 30秒

# 数据检查配置
DATA_LAKE_MESSAGE_COLLECTION = 'dataLakeMessage'

# 状态检查
REQUIRED_STATUS = 2

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
