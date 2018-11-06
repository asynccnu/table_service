from service import app, web, loop
from service.database import setup_db
from service.apis import api
from service.logger.logger import Logger


tabledb, userdb = loop.run_until_complete(setup_db())
api['tabledb'] = tabledb
api['userdb'] = userdb


logger = Logger.makelogger("|logger|")
api['logger'] = logger
api['logger'].info("Service Started.")

if __name__ == '__main__':
    web.run_app(app)
