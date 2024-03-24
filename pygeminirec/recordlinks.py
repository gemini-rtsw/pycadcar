
class RecordLinks:
    def __init__(self, parent=None):
        self.records = []

    def has_records(self):
        return len(self.records) > 0
    
    async def add_record_link(self, record):
        self.records.append(record)


    async def execute_on_all(self, command_func, **kwargs):
        # Check if the command_func is callable and exists
        if not callable(command_func):
            print(f"Command function does not exist or is not callable: {command_func}")
            return Result.ERROR, "Not Callable", self  # Or another appropriate value indicating failure

        # Execute command_func on self and check the result
        result, ret_mess = await command_func(self, **kwargs)
        if result is Result.ERROR:  
            return result, ret_mess, self  # Halt execution and return Result.ERROR

        # Recursively execute on all connected records
        for record in self.records:
            # Execute command_func on each record and halt if any returns Result.ERROR
            result, ret_mess, ret_cad = await record.records.execute_on_all(command_func, **kwargs)
            if result is Result.ERROR:
                return result, ret_mess, ret_cad  # Halt execution and return Result.ERROR

        # If execution reaches here, it means all CADs were successful
        return Result.SUCCESS, ret_mess, None  
