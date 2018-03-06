import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or 'localhost'
MONGOPORT = int(os.getenv('MONGOPORT') or '27017')

async def setup_db():
    client = AsyncIOMotorClient(MONGOHOST, MONGOPORT)
    tabledb = client['tabledb_2018_03_06']  # 存储信息门户课表 为了更新缓存调整了数据库名称
    userdb = client['userdb_2018_2']    # 存储自定义课表
    tablecol = tabledb['tables'] # 信息门户课表集合
    usercol = userdb['users']    # 自定义课表集合
    return tabledb, userdb
