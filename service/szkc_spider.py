import asyncio
import aiohttp
import os
import time
import json

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
    res = []
    async with aiohttp.ClientSession(headers = headers,
                                     cookies = cookies) as session:
        async with session.post(table_url, data = payload) as resp:
            try :
                json_data = await resp.json()
            except json.decoder.JSONDecodeError :
                return res
            for each in json_data['items'] :
                #day_dict = {'星期一':{},'星期二':{},'星期三':{},'星期四':{},'星期五':{},'星期六':{},'星期日':{}}
                day_dict = {}
                t_info = each['sksj']                                # 星期一第1-2节{6周};星期一第1-2节{7周};星期一第1-2节{8周};星期一第1-2节{9周}
                oneday_info = t_info.split(';')
                for oneday in oneday_info :                          # 星期一第1-2节{6周}
                    whichday = oneday[:3]
                    if whichday not in day_dict:
                        day_dict[whichday] = {}
                    k_index = oneday.find("{")
                    zhou_index = oneday.find("}")
                    _weeks = oneday[k_index + 1:zhou_index]           # 11周，10-13周，或10-5周（双）
                    week_list = getweek(_weeks)                       # ['10', '11', '12', '13'] ['11-12']

                    di_index = oneday.find("第")
                    jie_index = oneday.find("节")
                    times = oneday[di_index + 1:jie_index]  # 1-4,7-10
                    times_ = times.split(',')                         # ['1-4', '7-10']

                    for times in times_ :                             # ['1-2','4-5']
                        if times not in day_dict[whichday] :
                            day_dict[whichday][times] = []
                        day_dict[whichday][times] += week_list
                        day_dict[whichday][times] = list(set(day_dict[whichday][times]))              # 去除重复
                for day, time_ in day_dict.items():
                    for times, week_list in time_.items() :

                        week_list = [int(i) for i in week_list]           # 给week排序
                        week_list.sort()
                        week_list = [str(i) for i in week_list]

                        times = times.split('-')  # ['1','2']
                        start = int(times[0])
                        during = int(times[1]) - int(times[0]) + 1
                        teacher = each['jsxm'].split(',')
                        res_teacher = []
                        for t in teacher:
                            if '/' in t:
                                res_teacher.append(t.split('/')[1])
                            else:
                                res_teacher.append(t)
                        one = {
                            'course': each['kcmc'],
                            'teacher': ','.join(res_teacher),
                            'place': each['jxdd'],
                            'day': day,
                            'start': start,
                            'during': during,
                            "weeks": ",".join(week_list),
                            'remind': False,
                        }
                        print(one)
                        res.append(one)
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
   # if ',' in _weeks:
    _weeks = _weeks.split(',')
    for item in _weeks:
        #print(item)
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
    return week_list

if __name__ == '__main__' :
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_szkc_table(2018,3,2016210813))
    loop.close()

