import urllib.request
import time

t0 = time.time()
req = urllib.request.Request(
    'http://10.176.227.19/api/mode',
    headers={
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type',
        'Origin': 'http://10.176.227.19'
    },
    method='OPTIONS'
)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print('Status:', resp.status, 'Time:', time.time() - t0)
        print('Headers:', dict(resp.headers))
        print('Body:', resp.read().decode())
except Exception as e:
    print('Failed:', e, 'Time:', time.time() - t0)
