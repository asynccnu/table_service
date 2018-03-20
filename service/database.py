import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or '39.108.79.110'
MONGOPORT = int(os.getenv('MONGOPORT') or '27020')

async def setup_db():
    client = AsyncIOMotorClient(MONGOHOST, MONGOPORT)
    tabledb = client['tabledb_with_szkc_2018_3']  # 存储信息门户课表
    userdb = client['userdb_2018_1']    # 存储自定义课表
    tablecol = tabledb['tables'] # 信息门户课表集合
    usercol = userdb['users']    # 自定义课表集合
    szcol = tabledb['szkcs']
    return tabledb, userdb
