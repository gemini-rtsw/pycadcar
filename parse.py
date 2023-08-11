from typing import List

def convert_recordtype_to_pvgroup(recordtype_content: str) -> str:
    dbf_to_channel_type = {
        'DBF_STRING': 'ChannelType.CHAR',
        'DBF_MENU': 'ChannelType.ENUM',
    }

    def get_channel_type(dbf_type: str) -> str:
        return dbf_to_channel_type.get(dbf_type, 'ChannelType.CHAR')

    lines = recordtype_content.split('\n')
    pvgroup_content = []
    inside_field = False
    field_name = ""
    field_dtype = ""
    field_size = 0
    field_prompt = ""

    for line in lines:
        line = line.strip()
        if line.startswith('field('):
            inside_field = True
            _, rest = line.split('(', 1)
            field_name, field_dtype = rest[:-2].split(', ')
            field_dtype = field_dtype.split(')')[0]
        elif inside_field and line.startswith('prompt('):
            field_prompt = line.split('"')[1]
        elif inside_field and line.startswith('size('):
            field_size = int(line.split('(')[1][:-1])
        elif inside_field and line == '}':
            inside_field = False
            channel_type = get_channel_type(field_dtype)
            pvproperty_line = f"{field_name.lower()} = pvproperty(name='{field_name}',\n"
            pvproperty_line += f"                             dtype={channel_type},\n"
            pvproperty_line += f"                             max_length={field_size},\n"
            pvproperty_line += f"                             report_as_string=True,\n"
            pvproperty_line += f"                             doc='{field_prompt}')\n"
            pvgroup_content.append(pvproperty_line)

    return '\n'.join(pvgroup_content)

def main(input_file: str, output_file: str):
    with open(input_file, 'r') as file:
        recordtype_content = file.read()

    converted_content = convert_recordtype_to_pvgroup(recordtype_content)

    with open(output_file, 'w') as file:
        file.write(converted_content)

    print(f"Conversion completed. Output written to {output_file}")

if __name__ == "__main__":
    input_file = 'recordtype.txt'  # Change to your input file path
    output_file = 'pvgroup.txt'    # Change to your output file path
    main(input_file, output_file)
