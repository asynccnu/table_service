import os
from aiohttp import web
from aiohttp.web import Response
from .spider import get_table
from .decorator import require_info_login

api = web.Application()

# 课程id对于每个用户不重复即可
@require_info_login # 避免伪造查询请求
async def get_table_api(request, s, sid, ip):
    """
    课表查询API
    """
    xnm = os.getenv('XNM')
    xqm = os.getenv('XQM')
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    document = await tabledb.tables.find_one({'sid': sid})
    userdoc = await userdb.users.find_one({'sid': sid})
    usertables = []
    if userdoc:
        usertables = userdoc['table']
    if not document:
        # 用户第一次请求, 爬取信息门户课表并写入数据库
        tables = await get_table(s, sid, ip, xnm, xqm)
        if tables:
            for index, item in enumerate(tables):
                tables[index]['id'] = str(index) # 分配id
                tables[index]['color'] = index-4*(index//4) # 分配color
            await tabledb.tables.insert_one({'sid': sid, 'table': tables})
            return web.json_response(tables+usertables)
        return web.json_response({'error': 'null'})
    return web.json_response(document['table']+usertables)
    
@require_info_login
async def add_table_api(request, s, sid, ip):
    """
    添加课程API(添加用户自定义课程)
    """
    data = await request.json()
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    table = await tabledb.tables.find_one({'sid': sid})
    user = await userdb.users.find_one({'sid': sid})
    user_table = []; table_table = []
    if user:
        user_table = user['table']
    if table:
        table_table = table['table']
    tables = user_table + table_table
    item_ids = [int(item['id']) for item in tables]
    max_id = max(item_ids)
    new_json = {'id': str(max_id+1), 'color': 0}
    new_json.update(data)
    user_table.append(new_json)
    if user:
        await userdb['users'].update_one({'sid': sid}, {'$set': {'table': user_table}})
    else:
        await userdb['users'].insert_one({'sid': sid, 'table': user_table})
    return web.json_response({'id': max_id+1})

@require_info_login
async def del_table_api(request, s, sid, ip):
    """
    删除课程API/(可以)删除信息门户课程
    """
    id = request.match_info.get('id')
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    user = await userdb.users.find_one({'sid': sid})
    table = await tabledb.tables.find_one({'sid': sid})
    table_table = []; user_table = []
    if table:
        table_table = table['table']
    if user:
        user_table = user['table']
    for index, item in enumerate(table_table):
        if str(id) == item['id']:
            del table_table[index]
            await tabledb['tables'].update_one({'sid': sid}, {'$set': {'table': table_table}})
            return Response(body=b'{}',
                content_type='application/json', status=200
            )
    for index, item in enumerate(user_table):
        if str(id) == item['id']:
            del user_table[index]
            await userdb['users'].update_one({'sid': sid}, {'$set': {'table': user_table}})
            return Response(body=b'{}',
                content_type='application/json', status=200
            )
    return Response(body=b'{}',
        content_type='application/json', status=404
    )
    
@require_info_login
async def update_table_api(request, s, sid, ip):
    """
    更新课程API/自定义/信息门户课程
    """
    find = False
    id = request.match_info.get('id')
    data = await request.json()
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    user = await userdb.users.find_one({'sid': sid})
    table = await tabledb.tables.find_one({'sid': sid})
    table_table = []; user_table = []

    def update_table(tables, find): # 闭包
        for index, item in enumerate(tables):
            if str(id) == item['id']:
                color = tables[index]['color']
                tables[index] = data;
                tables[index]['id'] = str(id)
                tables[index]['color'] = color
                find = True; break
        return tables, find

    if table:
        table_table = table['table']
        table_table, find = update_table(table_table, find)
        if find:
            await tabledb['tables'].update_one({'sid': sid}, {'$set': {'table': table_table}})

    if user and not find:
        user_table = user['table']
        user_table, find = update_table(user_table, find)
        if find:
            await userdb['users'].update_one({'sid': sid}, {'$set': {'table': user_table}})

    if find:
        return Response(body=b'{}', content_type='application/json', status=200)
    return Response(body=b'{}', content_type='application/json', status=404)

api.router.add_route('GET', '/table/', get_table_api, name='get_table_api')
api.router.add_route('POST', '/table/', add_table_api, name='add_table_api')
api.router.add_route('DELETE', '/table/{id}/', del_table_api, name='del_table_api')
api.router.add_route('PUT', '/table/{id}/', update_table_api, name='updatei_table_api')
