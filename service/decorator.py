import json
import functools
import aiohttp
from aiohttp.web import Response, json_response

def require_info_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        BIGipServerpool_jwc_xk = req_headers.get("Bigipserverpool_Jwc_Xk")
        JSESSIONID = req_headers.get("Jsessionid")
        sid = req_headers.get("Sid")
        err_msg = "missing "
        authorized = True
        if not BIGipServerpool_jwc_xk:
            err_msg += "BIGipServerpool_jwc_xk: %s " % str(BIGipServerpool_jwc_xk); authorized = False
        if not JSESSIONID:
            err_msg += "JSESSIONID: %s " % str(JSESSIONID); authorized = False
        if not sid:
            err_msg += "Sid: %s" % str(sid); authorized = False
        if not authorized:
            return json_response(data={"err_msg": err_msg}, status=401)
        cookies = {'BIGipServerpool_jwc_xk': BIGipServerpool_jwc_xk, 'JSESSIONID': JSESSIONID}
        return await f(request, cookies, sid, None, *args, **kwargs)
    return decorator
