"""Isolated manual browser test: deny outbound network except loopback AI.
Run from project root: .venv/bin/python scripts/offline_server.py
Does not disconnect the user's computer or alter production data.
"""
import os, sys, socket, tempfile
from pathlib import Path
from contextlib import nullcontext
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(MODE='trail', MONGODB_URI='', BASECAMP_URL='', SYNC_TOKEN='', ELEVENLABS_API_KEY='', SENTRY_DSN='', SERPAPI_API_KEY='')
allowed={'localhost','127.0.0.1','::1'}
original_connect=socket.socket.connect
original_connect_ex=socket.socket.connect_ex
original_dns=socket.getaddrinfo
blocked=[]
def guard(address):
    if isinstance(address,tuple) and address[0] not in allowed:
        blocked.append(str(address[0]));raise OSError('Offline test: non-loopback network blocked')
def connect(self,address):
    guard(address);return original_connect(self,address)
def connect_ex(self,address):
    guard(address);return original_connect_ex(self,address)
def dns(host,*args,**kwargs):
    if host is not None and host not in allowed:
        blocked.append(str(host));raise OSError('Offline test: external DNS blocked')
    return original_dns(host,*args,**kwargs)
socket.socket.connect=connect
socket.socket.connect_ex=connect_ex
socket.getaddrinfo=dns
if __name__=='__main__':
    existing=os.getenv('OFFLINE_TEST_DATA_DIR')
    with (nullcontext(existing) if existing else tempfile.TemporaryDirectory(prefix='trail-offline-')) as directory:
        os.environ['DATA_DIR']=directory
        from backend.main import app
        @app.get('/api/offline-test')
        def proof():return {'outbound_policy':'loopback only','blocked_attempts':len(blocked)}
        # Register the test-only route before the production SPA catch-all.
        app.router.routes.insert(0,app.router.routes.pop())
        try:socket.create_connection(('example.com',443),timeout=1)
        except OSError:print('Verified external network is blocked.',flush=True)
        import uvicorn
        uvicorn.run(app,host='127.0.0.1',port=8004,workers=1)
