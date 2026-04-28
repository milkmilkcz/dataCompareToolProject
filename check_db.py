#!/usr/bin/env python3
"""
检查数据库中dataLakeMessage集合的数据结构
"""

import sys
import os

# 添加项目��目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from data_validation_tool.core.database import get_db_connection

def check_database():
    conn = get_db_connection()
    if conn.connect():
        db = conn.get_database()

        print(f'连接到数据库: {db.name}')
        print(f'数据库中的所有集合: {db.list_collection_names()}')

        # 检查dataLakeMessage集合
        if 'dataLakeMessage' in db.list_collection_names():
            collection = db.dataLakeMessage
            count = collection.count_documents({})
            print(f'\ndataLakeMessage 集合文档数量: {count}')

            if count > 0:
                print('\n前3个文档:')
                docs = list(collection.find().limit(3))
                for i, doc in enumerate(docs, 1):
                    print(f'\n文档 {i}:')
                    print(f'  _id: {doc.get("_id")}')
                    print(f'  bizTime: {doc.get("bizTime")} (类型: {type(doc.get("bizTime"))})')
                    print(f'  msgHead: {doc.get("msgHead")}')
                    print(f'  policyNum: {doc.get("policyNum")}')
                    print(f'  status: {doc.get("status")}')

                    # 检查bizTime格式
                    biztime = doc.get('bizTime')
                    if hasattr(biztime, 'year'):
                        print(f'  bizTime格式正确: {biztime.year}-{biztime.month:02d}-{biztime.day:02d} {biztime.hour:02d}:{biztime.minute:02d}:{biztime.second:02d}')
                    else:
                        print(f'  bizTime格式可能有问题: {biztime}')
            else:
                print('dataLakeMessage ���合为空')

                # 检查是否有其他可能的数据集合
                print('\n检查其他集合是否有数据:')
                for coll_name in db.list_collection_names():
                    if coll_name != 'dataLakeMessage':
                        coll = db[coll_name]
                        coll_count = coll.count_documents({})
                        if coll_count > 0:
                            print(f'  {coll_name}: {coll_count} 条记录')
        else:
            print('dataLakeMessage 集合不存在')

        conn.close()
    else:
        print('数据库连接失败')

if __name__ == '__main__':
    check_database()
