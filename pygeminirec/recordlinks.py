
import sys
from enum import IntEnum, Enum


class RecordLinks:
    def __init__(self, parent=None):
        self.records = []

    def has_records(self):
        return len(self.records) > 0
    
    async def add_record_link(self, record):
        self.records.append(record)


# only implemented for one layer of CAD/CAR any more need work
        
    async def execute_on_all(self, caller, command_func_name, reverse=False, **kwargs):
        
        # Determine the iteration order based on the reverse flag
        records_iterable = reversed(self.records) if reverse else self.records


        for record in records_iterable:
            print(f"Executing commands recursively on {record.prefix}")

            # Depending on the caller, we select the appropriate RecordLinks instance
            records_to_process = getattr(record, caller)

            # If not reversing, process the current record's command first (head recursion)
            if not reverse:
                result, ret_mess = await self.process_current_record(record, command_func_name, **kwargs)
                if result <= 0:
                    return result, ret_mess, record

            # Recursively call execute_on_all on the selected records_to_process
            recursive_result, recursive_message, _ = await records_to_process.execute_on_all(caller, command_func_name, reverse=reverse, **kwargs)
            if recursive_result <= 0:
                return recursive_result, recursive_message, record

            # If reversing, process the current record's command after the recursive call (tail recursion)
            if reverse:
                result, ret_mess = await self.process_current_record(record, command_func_name, **kwargs)
                if result <= 0:
                    return result, ret_mess, record

        print("HAWI need to fix this 1 is returned but need to return val/clid")
        return 1, "All sub records processed successfully", None

    async def process_current_record(self, record, command_func_name, **kwargs):
        # Retrieve and execute the command method on the current record
        if hasattr(record, command_func_name):
            command_method = getattr(record, command_func_name)
            if callable(command_method):
                print(f"Executing command on {record.prefix}")
                return await command_method(**kwargs)
        else:
            print(f"Command function {command_func_name} does not exist on record {record}")
            return 0, "Method Not Found", record
