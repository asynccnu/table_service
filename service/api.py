import os
from aiohttp import web
from aiohttp.web import Response
from .spider import get_table
from .decorator import require_info_login

api = web.Application()

# 现在信息门户课程和用户自定义课程是分开存储的
# 存储结构如下
# tabledb->tables->{'_id': object(hash), 'sid': basestring, 'table': [{k:v}...]}
# userdb->users->{'_id': object(hash), 'sid': basestring, 'table': [{k:v}...]}
# 可以做数据导出/导入
# 因为目前是微服务, 为了低耦合, 服务的副本共享一个单独的mongo数据库client
@require_info_login # 避免伪造查询请求
async def get_table_api(request, s, sid, pwd, ip):
    """
    课表查询API
    """
    xnm = os.getenv('XNM')
    xqm = os.getenv('XQM')
    tabledb = request.app['tabledb']
    document = await tabledb.tables.find_one({'sid': sid})
    if not document:
        # 用户第一次请求, 爬取信息门户课表并写入数据库
        tables = await get_table(s, sid, ip, xnm, xqm) # list
        if tables:
            await tabledb.tables.insert_one({'sid': sid, 'table': tables})
            return web.json_response(tables)
        return web.json_response({'error': 'null'})
    return web.json_response({'hack': 'fccnu'}) # ?
    
@require_info_login
async def add_table_api(request, s, sid, pwd, ip):
    """
    添加课程API
    """
    pass

@require_info_login
async def del_table_api(request, s, sid, pwd, ip):
    """
    删除课程API
    """
    pass

@require_info_login
async def put_table_api(request, s, sid, pwd, ip):
    """
    更新课程API
    """
    pass

api.router.add_route('POST', '/table/', get_table_api, name='get_table_api')
