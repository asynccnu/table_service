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

sid = os.getenv('ADMIN_SID')
pwd = os.getenv('ADMIN_PWD')

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
                new_data = each['sksj'].split(';')
                #print(new_data)
                #print(each['sksj'])
                week_list = []
                for each_time in new_data :
                    di_index = each_time.find("第")
                    jie_index = each_time.find("节")
                    times = each_time[di_index+1:jie_index]
                    times = times.split('-')
                    start = int(times[0])
                    during  = int(times[1]) - int(times[0]) + 1

                    k_index = each_time.find("{")
                    zhou_index = each_time.find("}")
                    _weeks = each_time[k_index+1:zhou_index]
                    #week_list = []
                    #print(_weeks)
                    if ',' in _weeks :
                        _weeks = _weeks.split(',')
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


if __name__ == '__main__' :
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_szkc_table(2017,12,2017211077))
    loop.close()

