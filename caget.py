import sys
from caproto.sync.client import read

if len(sys.argv) != 2:
    print("Usage: python caget.py <channel_name>")
    sys.exit(1)

channel_name = sys.argv[1]
response = read(channel_name)
print(response.data[0])
