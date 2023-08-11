import sys
from ast import literal_eval
from caproto.sync.client import write, read

if len(sys.argv) != 3:
    print("Usage: python caput.py <channel_name> <value>")
    sys.exit(1)

channel_name = sys.argv[1]
value_str = sys.argv[2]


try:
    value = literal_eval(value_str)
except (ValueError, SyntaxError):
    value = value_str

# Write the value to the channel
write(channel_name, value)

# Read the value back to verify and echo
response = read(channel_name)
new_value = response.data[0]
print(f'{channel_name} {new_value}')
