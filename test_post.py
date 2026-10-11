import urllib.request
import time

t0 = time.time()
data = b'{"mode":"BT"}'
req = urllib.request.Request(
    'http://10.176.227.19/api/mode',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print('Status:', resp.status, 'Time:', time.time() - t0)
        print('Body:', resp.read().decode())
except Exception as e:
    print('Failed:', e, 'Time:', time.time() - t0)
