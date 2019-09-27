import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or 'localhost'
MONGOPORT = int(os.getenv('MONGOPORT') or '27017')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME') or "muxi"
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD') or "nopassword"
TABLEDB = os.getenv('TABLEDB') or 'tabledb'
USERDB = os.getenv('USERDB') or 'userdb'

async def setup_db():
    # client = AsyncIOMotorClient(MONGODB_HOST, MONGODB_PORT)
    mongo_uri = "mongodb://{}:{}@{}:{}".format(MONGODB_USERNAME, MONGODB_PASSWORD, MONGOHOST, MONGOPORT)
    print(mongo_uri)
    client = AsyncIOMotorClient(mongo_uri)
    tabledb = client[TABLEDB]  # 存储信息门户课表
    userdb = client[USERDB]    # 存储自定义课表
    tablecol = tabledb['tables'] # 信息门户课表集合
    usercol = userdb['users']    # 自定义课表集合
    szcol = tabledb['szkcs']
    return tabledb, userdb
