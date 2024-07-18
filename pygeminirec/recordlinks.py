
import sys
import inspect
from enum import IntEnum, Enum

debug_mode = False

def debug_print(message):
    if debug_mode:
        debug_print("DEBUG:", message)

class RecordLinks:
    def __init__(self, parent=None):
        self.records = []

    def has_records(self):
        return len(self.records) > 0
    
    async def add_record_link(self, record):
        self.records.append(record)

    def get_by_declaration_name(self, name):
        caller_frame = inspect.currentframe().f_back
        locals_in_caller = caller_frame.f_locals
        for obj_name, obj in locals_in_caller.items():
            if obj_name == name and obj in self.records:
                return obj
        return None  

    def get_idle_override(self):
        for record in self.records:
            if record.idle_override == True:
                return record
        return None

        
    async def execute_on_all(self, caller, command_func_name, reverse=False, **kwargs):
        
        # Determine the iteration order based on the reverse flag
        records_iterable = reversed(self.records) if reverse else self.records


        for record in records_iterable:
            debug_print(f"Executing commands recursively on {record.prefix}")

            # Depending on the caller, we select the appropriate RecordLinks instance either cads or cars
            records_to_process = getattr(record, caller)

            # If not reversing, process the current record's command first (head recursion)
            if not reverse:
                result = await self.process_current_record(record, command_func_name, **kwargs)
                if result <= 0:
                    return result, record

            # Recursively call execute_on_all on the selected records_to_process
            recursive_result, recursive_record = await records_to_process.execute_on_all(caller, command_func_name, reverse=reverse, **kwargs)
            if recursive_result <= 0:
                return recursive_result, recursive_record

            # If reversing, process the current record's command after the recursive call (tail recursion)
            if reverse:
                result = await self.process_current_record(record, command_func_name, **kwargs)
                if result <= 0:
                    return result, record

        return True, None

    async def process_current_record(self, record, command_func_name, **kwargs):
        # Retrieve and execute the command method on the current record
        if hasattr(record, command_func_name):
            command_method = getattr(record, command_func_name)
            if callable(command_method):
                debug_print(f"Executing command on {record.prefix}")
                return await command_method(**kwargs)
        
        debug_print(f"Command function {command_func_name} does not exist on record {record}")
        record.errored_record = record
        return False

