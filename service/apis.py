import os
from aiohttp import web
from aiohttp.web import Response
from .spider import get_table
from .szkc_spider import get_szkc_table
from .decorator import require_info_login, require_sid

api = web.Application()


async def get_table_from_ccnu(tabledb,s, sid, ip, xnm, xqm):
    """
    优先从信息门户获取，信息门户失败再从缓存课表
    :return:
    """
    # 从信息门户获取
    tables = await get_table(s, sid, ip, xnm, xqm)
    # 从信息门户获取成功
    if tables:
        for index, item in enumerate(tables):
            tables[index]['id'] = str(index+1) # 分配id
            tables[index]['color'] = index-4*(index//4) # 分配color
        # 写入mongo
        filter_ = {'sid':sid}
        replace_ = {'sid':sid, 'table':tables}
        ## await tabledb.tables.insert_one({'sid': sid, 'table': tables})
        await tabledb.tables.find_one_and_replace(filter_,replace_,upsert=True)
    # 信息门户获取失败
    else:
        # 从缓存中获取
        document = await tabledb.tables.find_one({'sid': sid})
        # 缓存中获取成功
        if document:
            tables = document['table']
        # 缓存获取失败
        else:
            tables = []

    return tables


async def get_table_from_cache(tabledb,s, sid, ip, xnm, xqm):
    """
    优选从缓存中获取，缓存失败再从信息门户获取
    :param tabledb:
    :return:
    """
    # 缓存从查找
    document = await tabledb.tables.find_one({'sid': sid})
    # 缓存中获取成功
    if document:
        tables = document['table']
    # 缓存中获取失败
    else:
        # 从信息门户中获取
        tables = await get_table(s, sid, ip, xnm, xqm)
        # 信息门户中获取成功
        if tables:
            for index, item in enumerate(tables):
                tables[index]['id'] = str(index + 1)  # 分配id
                tables[index]['color'] = index - 4 * (index // 4)  # 分配color
                # 写入mongo
            #await tabledb.tables.insert_one({'sid': sid, 'table': tables})
            filter_ = {'sid':sid}
            replace_ = {'sid':sid, 'table':tables}
            ## await tabledb.tables.insert_one({'sid': sid, 'table': tables})
            await tabledb.tables.find_one_and_replace(filter_,replace_,upsert=True)
        # 信息门户获取失败
        else:
            tables = []
    return tables


# 课程id对于每个用户不重复即可
@require_info_login # 避免伪造查询请求
async def get_table_api(request, s, sid, ip):
    """
    课表查询API
    """
    xnm = os.getenv('XNM') or 2018
    xqm = os.getenv('XQM') or 3
    # 是否处于改选时期
    table_change = os.getenv('ON_CHANGE') or True
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    document = await tabledb.tables.find_one({'sid': sid})
    userdoc = await userdb.users.find_one({'sid': sid})
    szkcdoc = await tabledb.szkcs.find_one({'sid':sid})
    usertables = []

    if userdoc:                                                          # 将 1，2，3，格式的数据改成星期一，星期二
        usertables_ = userdoc['table']
        weekday = {'1': '星期一', '2': '星期二', '3': '星期三', '4': '星期四', '5': '星期五', '6': '星期六', '7': '星期日'}
        for item in usertables_ :
            day_ = item['day']
            if weekday.get(day_) is not None:
                day_ = weekday[day_]
                item['day'] = day_
            usertables.append(item)


    """
    tables = []
    if not document:
        # 用户第一次请求, 爬取信息门户课表并写入数据库
        tables = await get_table(s, sid, ip, xnm, xqm)
        if tables:
            for index, item in enumerate(tables):
                tables[index]['id'] = str(index+1) # 分配id
                tables[index]['color'] = index-4*(index//4) # 分配color
            await tabledb.tables.insert_one({'sid': sid, 'table': tables})
            #return web.json_response(tables+usertables)
        else :
            return web.Response(body=b'{"error": "null"}', content_type='application/json', status=500)
    else :
        tables = document['table']

    """

    # 处于改选时期，从信息门户获取
    if table_change:
        tables = await get_table_from_ccnu(tabledb,s, sid, ip, xnm, xqm)
    else:
        tables = await get_table_from_cache(tabledb,s, sid, ip, xnm, xqm)

    if len(tables) == 0:
        return web.Response(body=b'{"error": "null"}', content_type='application/json', status=500)

    szkcs = []

    # 素质课网站挂了，所以先把素质课的spider关了
    """
    if not szkcdoc :
        # 用户第一次请求，爬取素质课，并写入数据库
        # 找出课表中的最大id，防止ID重复
        user_table = []
        table_table = []
        # 若不为第一次请求则可以从document中拿到，但是若是第一次请求
        # document是没有重新请求新的，故需要从tables中获取
        if document:
            table_table = document['table']
        else:
            table_table = tables
        if userdoc:
            user_table = userdoc['table']

        tables_ = table_table + user_table
        item_ids = [int(item['id']) for item in tables_]
        max_id = max(item_ids or [1])

        szkcs = await get_szkc_table(xnm,xqm,sid)
        #if szkcs :
        for index, item in enumerate(szkcs) :
            szkcs[index]['id'] = str(index+1+max_id)  # 要保证不重复
            szkcs[index]['color'] = index-4*(index//4)
        await tabledb.szkcs.insert_one({'sid':sid,'table':szkcs})
    else :
        szkcs = szkcdoc['table']
    """

    return web.json_response(tables+usertables+szkcs)


@require_sid
async def add_table_api(request, sid, ip):
    """
    添加课程API(添加用户自定义课程)
    """
    data = await request.json()
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    table = await tabledb.tables.find_one({'sid': sid})
    user = await userdb.users.find_one({'sid': sid})
    szkc = await tabledb.szkcs.find_one({'sid':sid})
    user_table = []; table_table = [] ; szkc_table = []
    if user:
        user_table = user['table']
    if table:
        table_table = table['table']
    if szkc:
        szkc_table = szkc['table']
    tables = user_table + table_table + szkc_table
    item_ids = [int(item['id']) for item in tables]
    max_id = max(item_ids or [1])
    new_json = {'id': str(max_id+1), 'color': 0}
    new_json.update(data) # 此时id不会被覆盖
    user_table.append(new_json)
    if user:
        await userdb['users'].update_one({'sid': sid}, {'$set': {'table': user_table}})
    else:
        await userdb['users'].insert_one({'sid': sid, 'table': user_table})
    return web.json_response({'id': max_id+1})

@require_info_login
async def del_table_api(request,s, sid, ip):
    """
    删除课程API/(可以)删除信息门户课程
    """
    id = request.match_info.get('id')
    tabledb = request.app['tabledb']
    userdb = request.app['userdb']
    user = await userdb.users.find_one({'sid': sid})
    table = await tabledb.tables.find_one({'sid': sid})
    szkc = await tabledb.szkcs.find_one({'sid':sid})
    table_table = []; user_table = []; szkc_table = []
    if table:
        table_table = table['table']
    if user:
        user_table = user['table']
    if szkc:
        szkc_table = szkc['table']
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
    for index, item, in enumerate(szkc_table):
        if str(id) == item['id']:
            del szkc_table[index]
            await tabledb['szkcs'].update_one({'sid':sid},{'$set': {'table':szkc_table}})
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
    szkc = await tabledb.szkcs.find_one({'sid':sid})
    table_table = []; user_table = [] ; szkc_table = []

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

    if szkc and not find:
        szkc_table = szkc['table']
        szkc_table, find = update_table(szkc_table,find)
        if find:
            await tabledb['szkcs'].update_one({'sid':sid}, {'$set': {'table': szkc_table}})

    if find:
        return Response(body=b'{}', content_type='application/json', status=200)
    return Response(body=b'{}', content_type='application/json', status=404)


async def get_table_api_tmp(request):
    """
    课表查询API
    """
    data = await request.json()
    sid = data['sid']
    #MONGOHOST = os.getenv('MONGOHOST')
    xnm = os.getenv('XNM')
    xqm = os.getenv('XQM')
    userdb = request.app['userdb']
    userdoc = await userdb.users.find_one({'sid': sid})
    usertables = []

    if userdoc:                                                          # 将 1，2，3，格式的数据改成星期一，星期二
        usertables_ = userdoc['table']
        for item in usertables_ :
            usertables.append(item)

    return web.json_response(usertables)


api.router.add_route('GET', '/table/', get_table_api, name='get_table_api')
api.router.add_route('POST', '/tmp/table/', get_table_api_tmp, name='get_table_api_tmp')
api.router.add_route('POST', '/table/', add_table_api, name='add_table_api')
api.router.add_route('DELETE', '/table/{id}/', del_table_api, name='del_table_api')
api.router.add_route('PUT', '/table/{id}/', update_table_api, name='updatei_table_api')
