import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://username:secret@localhost:27017/?authSource=admin"

TABLEDB = os.getenv('TABLEDB') or 'tabledb'
USERDB = os.getenv('USERDB') or 'userdb'

async def setup_db():
    # client = AsyncIOMotorClient(MONGODB_HOST, MONGODB_PORT)
    mongo_uri = MONGO_URI
    print(mongo_uri)
    client = AsyncIOMotorClient(mongo_uri)
    tabledb = client[TABLEDB]  # 存储信息门户课表
    userdb = client[USERDB]    # 存储自定义课表
    tablecol = tabledb['tables'] # 信息门户课表集合
    usercol = userdb['users']    # 自定义课表集合
    szcol = tabledb['szkcs']
    return tabledb, userdb
