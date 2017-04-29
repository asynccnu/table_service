import json
import functools
import aiohttp
from aiohttp.web import Response

def require_info_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        BIGipServerpool_jwc_xk = req_headers.get("Bigipserverpool_Jwc_Xk")
        JSESSIONID = req_headers.get("Jsessionid")
        sid = req_headers.get("Sid")
        if BIGipServerpool_jwc_xk and JSESSIONID and sid:
            cookies = {'BIGipServerpool_jwc_xk': BIGipServerpool_jwc_xk, 'JSESSIONID': JSESSIONID}
            return await f(request, cookies, sid, None, *args, **kwargs)
        else: return Response(
            body = b'', content_type = 'application/json',
            status = 401
        )
    return decorator
