import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or 'test_mongo3'
MONGOPORT = int(os.getenv('MONGOPORT') or '27017')
TABLEDB = os.getenv('TABLEDB') or 'tabledb'
USERDB = os.getenv('USERDB') or 'userdb'

async def setup_db():
    client = AsyncIOMotorClient(MONGOHOST, MONGOPORT)
    tabledb = client[TABLEDB]  # 存储信息门户课表
    userdb = client[USERDB]    # 存储自定义课表
    tablecol = tabledb['tables'] # 信息门户课表集合
    usercol = userdb['users']    # 自定义课表集合
    szcol = tabledb['szkcs']
    return tabledb, userdb
