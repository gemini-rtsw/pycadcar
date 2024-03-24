
import sys
from enum import IntEnum, Enum

class Result(IntEnum):
    ERROR = 0
    SUCCESS = 1


class RecordLinks:
    def __init__(self, parent=None):
        self.records = []

    def has_records(self):
        return len(self.records) > 0
    
    async def add_record_link(self, record):
        self.records.append(record)


# only implemented for one layer of CAD/CAR any more need work
        
    async def execute_on_all(self, command_func_name, **kwargs):

        # Iterate over each record in the list and execute the command_func on it
        for record in self.records:
            print(f"Checking command on {record.prefix}")

            # Retrieve the method by name from the record
            if hasattr(record, command_func_name):
                command_method = getattr(record, command_func_name)
                if callable(command_method):
                    # Execute the method with the provided kwargs
                    print(f"Executing command on {record.prefix}")
                    result, ret_mess = await command_method(**kwargs)
                    # If the method returns Result.ERROR, halt execution and return
                    if result is Result.ERROR:
                        return result, ret_mess, record
            else:
                print(f"Command function {command_func_name} does not exist on record {record}")
                return Result.ERROR, "Method Not Found", record

        # If all records have been processed without errors, return success
        return Result.SUCCESS, f"All sub records processed successfully", None
