import json
import aiohttp
from .logger.logger import Logger

logger = Logger.makelogger("|spider logger|")

test_url = "http://portal.ccnu.edu.cn/index_jg.jsp"
table_index_url = "http://xk.ccnu.edu.cn/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508&sessionUserKey=%s" # sqlmap

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

async def get_table(s, sid, ip, xnm, xqm):
#    s['UM_distinctid'] = s.get('BIGipServerpool_jwc_xk')
#    s.pop('BIGipServerpool_jwc_xk')
    logger.info("Cookie:"+str(s))
    
    table_url = table_index_url % sid
    payload = {'xnm': xnm, 'xqm': xqm}
    weekday = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
    try:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),
                cookies=s, headers=headers) as session:
            async with session.post(table_url, data=payload, timeout=3) as resp:
                logger.info("RespInfo:" + str(await resp.text()))

                json_data = await resp.json()
                # prase json_data
                kbList = json_data.get('kbList')
                kcList = []
                weeks_list = []
                for item in kbList:
                    _weeks = item.get('zcd')
                    weeks_list = tmp_get_week(_weeks)
                    #print(_weeks,weeks_list)
                    str_weeks_list = [str(i) for i in weeks_list]
                    _class = item.get('jcs').split('-')
                    s_class = int(_class[0])
                    e_class = int(_class[-1])
                    d_class = e_class - s_class + 1

                    day_ = item.get('xqjmc')                        # 将 1，2，3，格式的数据改成星期一，星期二
                    if weekday.get(day_) is not None :
                        day_ = weekday[day_]

                    teacher = item.setdefault('xm','').split("\n")[0]
                    _item_dict = {
                        'course': item.get('kcmc') or "",
                        'teacher': teacher,
                        'weeks': ','.join(str_weeks_list) or [],
                        'day': day_,
                        'start': s_class,
                        'during': d_class,
                        'place': item.get('xqmc') + item.get('cdmc'),
                        'remind': False
                    }
                    kcList.append(_item_dict)
                return(kcList)
    except Exception as e:
        logger.exception(repr(e))
        return None


def get_from_one_item(_weeks):
    week_list = []
    if '(' in _weeks:
        weeks = _weeks.split('(')
        time = weeks[0]
        mode = weeks[-1]
        _time = time.split('-')
        _start = int(_time[0])
        _last = int(_time[-1][:-1])
        if mode:  # 奇偶
            week_list = range(_start, _last + 1, 2)
    elif '-' in _weeks:
        weeks = _weeks.split('-')
        _start = int(weeks[0])
        _last = int(weeks[-1][:-1])
        week_list = range(_start, _last + 1)
    else:
        week_list = [int(_weeks[:-1])]

    return week_list


def tmp_get_week(_weeks):
    each_weeks = _weeks.split(',')
    week_lists = []
    for each in each_weeks:
        each_list = get_from_one_item(each)
        week_lists += each_list
    return week_lists
