import json
import aiohttp
from .logger.logger import Logger

logger = Logger.makelogger("|spider logger|")

test_url = "http://portal.ccnu.edu.cn/index_jg.jsp"
table_index_url = "http://122.204.187.6/kbcx/|delete|xskbcx_cxXsKb.html?gnmkdmKey=N253508&sessionUserKey=%s" # sqlmap

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

async def get_table(s, sid, ip, xnm, xqm):
    table_url = table_index_url % sid
    payload = {'xnm': xnm, 'xqm': xqm}
    weekday = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),
            cookies=s, headers=headers) as session:
        async with session.post(table_url, data=payload) as resp:
            try:
                json_data = await resp.json()
                # prase json_data
                kbList = json_data.get('kbList')
                kcList = []
                weeks_list = []
                for item in kbList:
                    _weeks = item.get('zcd')
                    if '(' in _weeks:
                        weeks = _weeks.split('(')
                        time = weeks[0]
                        mode = weeks[-1]
                        if ',' in time:
                            times = time.split(',')
                            weeks_list.append(times[0][:-1])
                            time = times[1]
                        _time = time.split('-')
                        _start = int(_time[0])
                        _last = int(_time[-1][:-1])
                        if mode: # 奇偶
                            weeks_list = range(_start, _last+1, 2)
                    elif ',' in _weeks:
                        weeks = _weeks.split(',')
                        weeks_list = []
                        for week in weeks:
                            if '-' in week:
                                _start = int(week.split('-')[0])
                                _last = int(week.split('-')[1][:-1])
                                _weeks_list = range(_start, _last+1)
                                weeks_list += _weeks_list
                            else:
                                weeks_list.append(week[:-1])
                    elif '-' in _weeks:
                        weeks = _weeks.split('-')
                        _start = int(weeks[0])
                        _last = int(weeks[-1][:-1])
                        weeks_list = range(_start, _last+1)
                    else:
                        weeks_list = [int(_weeks[:-1])]
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
