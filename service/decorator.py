import json
import functools
import aiohttp
from aiohttp.web import Response, json_response
from .logger.logger import Logger

decorator_logger = Logger.makelogger("|decorator logger|")

def require_info_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        BIGipServerpool_jwc_xk = req_headers.get("Bigipserverpool")
        JSESSIONID = req_headers.get("Jsessionid")
        sid = req_headers.get("Sid")
        err_msg = "missing "
        authorized = True
        if not BIGipServerpool_jwc_xk:
            err_msg += "BIGipServerpool: %s " % str(BIGipServerpool_jwc_xk); authorized = False
        if not JSESSIONID:
            err_msg += "JSESSIONID: %s " % str(JSESSIONID); authorized = False
        if not sid:
            err_msg += "Sid: %s" % str(sid); authorized = False
        if not authorized:
            return json_response(data={"err_msg": err_msg}, status=401)
        cookies = {'BIGipServerpool_jwc_xk': BIGipServerpool_jwc_xk, 'JSESSIONID': JSESSIONID}

        decorator_logger.info(str(sid) + " requested " + str(request.rel_url))
        return await f(request, cookies, sid, None, *args, **kwargs)
    return decorator


def require_sid(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        sid = req_headers.get("Sid")

        if not sid:
            err_msg = "missing Sid: %s" % str(sid)
            return json_response(data={"err_msg": err_msg}, status=401)

        decorator_logger.info(str(sid) + " requested " + str(request.rel_url))

        return await f(request, sid,  *args, **kwargs)
    return decorator
