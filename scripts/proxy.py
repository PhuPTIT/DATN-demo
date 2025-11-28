"""
Simple proxy to forward requests from port 8000 to 8001
"""
import asyncio
from aiohttp import web, ClientSession
import aiohttp

async def proxy_handler(request):
    """Forward requests from 8000 to 8001"""
    # Get the path and method
    path = request.path
    method = request.method
    
    # Get the body if POST/PUT
    try:
        body = await request.read()
    except:
        body = b''
    
    # Build target URL
    target_url = f"http://localhost:8001{path}"
    
    # Copy headers
    headers = dict(request.headers)
    headers.pop('Host', None)  # Remove Host header
    
    try:
        async with ClientSession() as session:
            async with session.request(
                method,
                target_url,
                data=body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                response_body = await resp.read()
                return web.Response(
                    body=response_body,
                    status=resp.status,
                    headers=resp.headers,
                    content_type=resp.content_type
                )
    except Exception as e:
        return web.Response(
            text=f"Proxy error: {str(e)}",
            status=502
        )

async def start_proxy():
    """Start proxy server on port 8000"""
    app = web.Application()
    app.router.add_route('*', '/{path_info:.*}', proxy_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    print("[PROXY] Proxy started on http://0.0.0.0:8000")
    print("[PROXY] Forwarding to http://localhost:8001")
    
    # Keep running
    await asyncio.sleep(3600000)

if __name__ == "__main__":
    asyncio.run(start_proxy())
