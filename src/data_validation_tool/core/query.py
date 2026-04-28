from datetime import datetime
import logging
from .database import get_db_connection
from .config import DATA_LAKE_MESSAGE_COLLECTION


logger = logging.getLogger(__name__)


class DataLakeMessageQuery:
    """DataLakeMessage 数据查询模块"""

    def __init__(self):
        self.conn = get_db_connection()
        self.collection = self.conn.get_collection(DATA_LAKE_MESSAGE_COLLECTION)

    def query_by_biztime_range(self, start_biztime, end_biztime):
        """
        按 bizTime 范围查询数据

        支持多种时间格式：
        - YYYY-MM-DD HH:MM:SS
        - YYYY-MM-DD HH:MM:SS.ssssss
        - YYYY-MM-DDTHH:MM:SS.sssZ (ISO格式)

        Args:
            start_biztime: 开始时间 (可以是字符串或datetime对象)
            end_biztime: 结束时间

        Returns:
            查询结果列表
        """
        try:
            # 定义多种时间格式
            time_formats = [
                '%Y-%m-%d %H:%M:%S',           # 2026-04-24 13:28:11
                '%Y-%m-%d %H:%M:%S.%f',        # 2026-04-24 13:28:11.946000
                '%Y-%m-%dT%H:%M:%S.%f%z',      # 2026-04-24T13:28:11.946+00:00
                '%Y-%m-%dT%H:%M:%S.%fZ',       # 2026-04-24T13:28:31.491Z
                '%Y-%m-%dT%H:%M:%SZ',          # 2026-04-24T13:28:31Z
                '%Y-%m-%dT%H:%M:%S.%f',        # 2026-04-24T13:28:31.491
                '%Y-%m-%dT%H:%M:%S',           # 2026-04-24T13:28:31
            ]

            # 转换时间格式
            def parse_datetime(time_value):
                if isinstance(time_value, str):
                    for fmt in time_formats:
                        try:
                            return datetime.strptime(time_value, fmt)
                        except ValueError:
                            continue
                    # 如果所有格式都失败，尝试移除末尾的Z或其他字符
                    if time_value.endswith('Z'):
                        time_value = time_value[:-1]
                        for fmt in time_formats:
                            try:
                                return datetime.strptime(time_value, fmt)
                            except ValueError:
                                continue
                    raise ValueError(f"无法解析时间格式: {time_value}")
                else:
                    return time_value

            start_dt = parse_datetime(start_biztime)
            end_dt = parse_datetime(end_biztime)

            # 如果开始时间和结束时间相同，改为精确到秒的范围查询
            if start_dt == end_dt:
                logger.info(f"开始时间和结束时间相同，使用精确到秒的范围查询: {start_biztime}")
                # 使用正则表达式匹配该秒的所有时间
                time_pattern = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
                regex_query = {
                    'bizTime': {'$regex': f'^{time_pattern}'}
                }
                results = list(self.collection.find(regex_query))
                if results:
                    logger.info(f"精确到秒��询到 {len(results)} 条数据 (bizTime 匹配 {time_pattern}*)")
                    return results
                # 如���精��查询没有结果，继续原始范围查询

            # 构建查询条件 - 支持字符串和datetime格式
            # 首先尝试datetime查询，如果没有结果则尝试字符串查询
            datetime_query = {
                'bizTime': {
                    '$gte': start_dt,
                    '$lte': end_dt
                }
            }

            results = list(self.collection.find(datetime_query))

            # 如果datetime查询没有结果，尝试字符串范围查询
            if not results:
                # 将时间转换为字符串进行比较
                start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')

                string_query = {
                    'bizTime': {
                        '$gte': start_str,
                        '$lte': end_str
                    }
                }
                results = list(self.collection.find(string_query))

            # 如果仍然没有结果，尝试使用正则表达式进行日期范围匹配
            if not results:
                # 构建日期范围的正则表达式
                start_date_str = start_dt.strftime('%Y-%m-%d')
                end_date_str = end_dt.strftime('%Y-%m-%d')

                # 如果是同一天，使用精确匹配
                if start_date_str == end_date_str:
                    date_pattern = f'^{start_date_str}'
                else:
                    # 如果是不同日期，使���范围匹配（这里简化处理，只匹配日期部分）
                    date_pattern = f'^({start_date_str}|{end_date_str})'

                regex_query = {
                    'bizTime': {'$regex': date_pattern}
                }
                results = list(self.collection.find(regex_query))

                # 进一步过滤时间范围
                if results:
                    filtered_results = []
                    for doc in results:
                        try:
                            doc_time = parse_datetime(doc.get('bizTime'))
                            if start_dt <= doc_time <= end_dt:
                                filtered_results.append(doc)
                        except:
                            # 如果无法解析时间，保留在结果中
                            filtered_results.append(doc)
                    results = filtered_results

            logger.info(f"查询到 {len(results)} 条数据 (bizTime 范围: {start_biztime} ~ {end_biztime})")
            return results

        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []

    def query_by_biztime_exact(self, biztime):
        """
        按确切的 bizTime 查询数据

        Args:
            biztime: 时间值

        Returns:
            查询结果列表
        """
        try:
            query = {'bizTime': biztime}
            results = list(self.collection.find(query))
            logger.info(f"查询到 {len(results)} 条数据 (bizTime = {biztime})")
            return results
        except Exception as e:
            logger.error(f"查询数据失���: {e}")
            return []

    def query_by_policy_num(self, policy_num):
        """
        按 policyNum 查询数据

        Args:
            policy_num: 保单号

        Returns:
            查询结果列表
        """
        try:
            query = {'policyNum': policy_num}
            results = list(self.collection.find(query))
            logger.info(f"查询到 {len(results)} 条数据 (policyNum = {policy_num})")
            return results
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []

