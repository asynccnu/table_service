import json
import functools
import aiohttp
from aiohttp.web import Response

def require_info_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        try:
            resp = await request.json()
        except json.decoder.JSONDecodeError:
            return Response(
                body = b'{"error": "info login service error"}',
                content_type = 'application/json',
                status = 500
            )
        if resp != {}:
            sid = resp.get('sid')
            pwd = resp.get('pwd')
            cookies = resp.get('cookie')
            return await f(request, cookies, sid, pwd, None, *args, **kwargs)
        else:
            return Response(body = b'', content_type = 'application/json',
                status = 403)
    return decorator
