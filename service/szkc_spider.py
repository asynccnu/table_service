import asyncio
import aiohttp
import os
import time

pre_url = "http://122.204.187.9/jwglxt"
pre_url2 = "http://122.204.187.9/jwglxt/xtgl/dl_loginForward.html?_t="
login_url = "http://122.204.187.9/jwglxt/xtgl/login_login.html"
table_url = "http://122.204.187.9/jwglxt/xkmdtj/xsgrpkgl_cxXsgrpkglJxbList.html?gnmkdmKey=N253015&sessionUserKey=muxi"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
}

sid = os.getenv('ADMIN_SID') or 'muxi'
pwd = os.getenv('ADMIN_PWD') or 'ihdmx123'


async def get_szkc_table(xnm, xqm, s):
    cookies = await login_szkc(sid, pwd)
    tlist = str(time.time()).split('.')
    t = tlist[0] + tlist[1][0:3]
    payload = {
        "filterKey" : "all",
        "filter_list[0]" : s,
        "xh_id" : s,
        "_search" : False,
        "nd" : t,
        "queryModel.showCount": 20,
        "queryModel.currentPage": 1,
        "queryModel.sortOrder": "asc",
        "time": 0,
        "queryModel.sortName" : "",
    }
    if xqm != "" :
        payload.update({"xqm_list[0]":xqm})
    if xnm != "" :
        payload.update({"xn_list[0]":xnm})
    #print(payload)
    res = []
    async with aiohttp.ClientSession(headers = headers,
                                     cookies = cookies) as session:
        async with session.post(table_url, data = payload) as resp:
            try :
                json_data = await resp.json()
            except JSONDecodeError :
                return res
            #print(json_data['items'])
            for each in json_data['items'] :
                #day_dict = {'星期一':{},'星期二':{},'星期三':{},'星期四':{},'星期五':{},'星期六':{},'星期日':{}}
                day_dict = {}
                #print(each)
                t_info = each['sksj']                                # 星期一第1-2节{6周};星期一第1-2节{7周};星期一第1-2节{8周};星期一第1-2节{9周}
                #print(t_info)
                oneday_info = t_info.split(';')
                #print(oneday_info)
                for oneday in oneday_info :                          # 星期一第1-2节{6周}
                    #print(oneday)
                    whichday = oneday[:3]
                    if whichday not in day_dict:
                        day_dict[whichday] = {}
                    k_index = oneday.find("{")
                    zhou_index = oneday.find("}")
                    _weeks = oneday[k_index + 1:zhou_index]           # 11周，10-13周，或10-5周（双）
                    #print(_weeks)
                    week_list = getweek(_weeks)                       # ['10', '11', '12', '13'] ['11-12']
                    #print(week_list)

                    di_index = oneday.find("第")
                    jie_index = oneday.find("节")
                    times = oneday[di_index + 1:jie_index]  # 1-4,7-10
                    # print(times)
                    times_ = times.split(',')                         # ['1-4', '7-10']
                    # print(oneday[:3],times_)

                    for times in times_ :                             # ['1-2','4-5']
                        #print(whichday,times)
                        if times not in day_dict[whichday] :
                            day_dict[whichday][times] = []
                        day_dict[whichday][times] += week_list
                        #print(day_dict)
                        """
                        times = times.split('-')                      # ['1','2']
                        start = int(times[0])
                        during = int(times[1]) - int(times[0]) + 1
                        #print(start,during)                          # 1, 2
                        one = {
                            'course': each['kcmc'],
                            'teacher': each['jsxm'],
                            'place': each['jxdd'],
                            'day': whichday,
                            'start': start,
                            'during': during,
                            "weeks": ",".join(week_list),
                            'remind': False,
                        }
                        res.append(one)
                        #print(one)
                        """
                #print(day_dict)
                for day, time_ in day_dict.items():
                    for times, week_list in time_.items() :
                        #print(times,week_list)
                    #print(time_)
                        times = times.split('-')  # ['1','2']
                        start = int(times[0])
                        during = int(times[1]) - int(times[0]) + 1
                        one = {
                            'course': each['kcmc'],
                            'teacher': each['jsxm'],
                            'place': each['jxdd'],
                            'day': day,
                            'start': start,
                            'during': during,
                            "weeks": ",".join(week_list),
                            'remind': False,
                        }
                        print(one)
                        res.append(one)

                """
                new_data = each['sksj'].split(';')
                #print(new_data)
                #print(each['sksj'])
                #week_list = []
                start_during = []
                res_week =[]
                for each_time in new_data :
                    di_index = each_time.find("第")
                    jie_index = each_time.find("节")
                    times = each_time[di_index+1:jie_index]
                    more_time = times.split(',')
                    res_time = []
                    print(more_time)
                    #start_during = []
                    for each_t in more_time:
                        res_time.append(each_t.split('-'))
                    for times in res_time:
                        #times = times.split('-')
                        #print(times)
                        tmp = []
                        start = int(times[0])
                        during  = int(times[1]) - int(times[0]) + 1
                        tmp.append(start)
                        tmp.append(during)
                        start_during.append(tmp)
                    #print(each_time)
                    k_index = each_time.find("{")
                    zhou_index = each_time.find("}")
                    _weeks = each_time[k_index+1:zhou_index]
                    week_list = []
                    #print(_weeks)

                    if ',' in _weeks :
                        _weeks = _weeks.split(',')
                        print(_weeks)
                        for item in _weeks :
                            if '-' in item:
                                if "周(双)" in item:
                                    tmp_week = item.split('-')
                                    _start = int(tmp_week[0])
                                    _end_list = tmp_week[1][:-1].split("周")
                                    _end = int(_end_list[0])
                                    _week_list = [str(i) for i in range(_start, _end + 1) if i % 2 == 0]
                                    week_list.extend(_week_list)
                                elif "周(单)" in item:
                                    tmp_week = item.split('-')
                                    _start = int(tmp_week[0])
                                    _end_list = tmp_week[1][:-1].split("周")
                                    _end = int(_end_list[0])
                                    _week_list = [str(i) for i in range(_start, _end + 1) if i % 2 == 1]
                                    week_list.extend(_week_list)
                                else:
                                    tmp_week = item.split('-')
                                    # print(tmp_week)
                                    _start = int(tmp_week[0])
                                    _end = int(tmp_week[1][:-1])
                                    # print(_start,_end)
                                    _week_list = [str(i) for i in range(_start, _end + 1)]
                                    week_list.extend(_week_list)
                                # print(week_list)
                            else :
                                week_list.append(item[:-1])
                    else :
                        if '-' in  _weeks :
                            tmp_week = _weeks.split('-')
                            _start = int(tmp_week[0])
                            _end = int(tmp_week[1][:-1])
                            _week_list = [str(i) for i in range(_start,_end+1)]
                            week_list.extend(_week_list)
                        else :
                            week_list.append(_weeks[:-1])

                for each_start in start_during :
                    #print(each_start)
                    pass
                    one = {
                                    'course': each['kcmc'],
                                    'teacher': each['jsxm'],
                                    'place': each['jxdd'],
                                    'day': each['sksj'][:3],
                                    'start' : start,
                                    'during' : during,
                                    "weeks" : ",".join(week_list),
                                    'remind' : False,
                                }
                    res.append(one)
                    print(one)
                    """
            return res
        return None


async def login_szkc(sid, pwd):
    async with aiohttp.ClientSession(cookie_jar = aiohttp.CookieJar(unsafe=True),
                                     headers = headers) as session:
        async with session.get(pre_url) as resp:
            if resp.status == 200:
                tlist = str(time.time()).split('.')
                t = tlist[0] + tlist[1][0:3]
                async with session.get(pre_url2 + t) as resp2:
                    if resp2.status == 200:
                        payload = {
                            "yhm": sid,
                            "mm": pwd,
                            "yzm":""
                        }
                        async with session.post(login_url, data = payload) as resp3:
                            resp_text = await resp3.text()
                            loginok = False
                            msg = ""
                            if "用户名或密码不正确" in resp_text:
                                msg = "用户名或密码错误"
                            elif "xskbcx_cxXskbcxIndex.html" in resp_text:
                                loginok = True
                            elif "登录超时" in resp_text:
                                msg = "登录超时"
                            else:
                                msg = "未知错误"

                            cookies = {}
                            if loginok:
                                for cookie in session.cookie_jar:
                                    cookies[cookie.key] = cookie.value
                                print(cookies)
                                return cookies
                            else:
                                print(msg)
                                return {"msg":msg}


def getweek(_weeks) :
    """
    11周，10-13周，或10-5周（双）
    :param _weeks:
    :return:
    """
    week_list = []
    if ',' in _weeks:
        _weeks = _weeks.split(',')
        print(_weeks)
        for item in _weeks:
            if '-' in item:
                if "周(双)" in item:
                    tmp_week = item.split('-')
                    _start = int(tmp_week[0])
                    _end_list = tmp_week[1][:-1].split("周")
                    _end = int(_end_list[0])
                    _week_list = [str(i) for i in range(_start, _end + 1) if i % 2 == 0]
                    week_list.extend(_week_list)
                elif "周(单)" in item:
                    tmp_week = item.split('-')
                    _start = int(tmp_week[0])
                    _end_list = tmp_week[1][:-1].split("周")
                    _end = int(_end_list[0])
                    _week_list = [str(i) for i in range(_start, _end + 1) if i % 2 == 1]
                    week_list.extend(_week_list)
                else:
                    tmp_week = item.split('-')
                    # print(tmp_week)
                    _start = int(tmp_week[0])
                    _end = int(tmp_week[1][:-1])
                    # print(_start,_end)
                    _week_list = [str(i) for i in range(_start, _end + 1)]
                    week_list.extend(_week_list)
                # print(week_list)
            else:
                week_list.append(item[:-1])
    else:
        if '-' in _weeks:
            tmp_week = _weeks.split('-')
            _start = int(tmp_week[0])
            _end = int(tmp_week[1][:-1])
            _week_list = [str(i) for i in range(_start, _end + 1)]
            week_list.extend(_week_list)
        else:
            week_list.append(_weeks[:-1])
    return week_list

if __name__ == '__main__' :
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_szkc_table(2017,12,2017211761))
    loop.close()

