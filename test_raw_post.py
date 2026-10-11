import socket
import time

s = socket.socket()
s.settimeout(3)
s.connect(('10.176.227.19', 80))
raw_http = b'POST /api/mode HTTP/1.1\r\nHost: 10.176.227.19\r\nContent-Type: application/json\r\nContent-Length: 13\r\n\r\n{"mode":"BT"}'
t0 = time.time()
s.sendall(raw_http)
try:
    resp = s.recv(4096)
    print(f'Response in {time.time()-t0:.2f} sec:')
    print(resp.decode(errors='ignore'))
except Exception as e:
    print(f'FAILED / HANG in {time.time()-t0:.2f} sec: {e}')
s.close()
