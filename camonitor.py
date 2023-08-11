import sys
from caproto.threading.client import Context

if len(sys.argv) != 2:
    print("Usage: python camonitor.py <channel_name>")
    sys.exit(1)

channel_name = sys.argv[1]

def callback(sub, response):
    print(f'{channel_name} {response.data[0]}')

with Context() as context:
    pv, = context.get_pvs(channel_name)
    sub = pv.subscribe()
    sub.add_callback(callback)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
