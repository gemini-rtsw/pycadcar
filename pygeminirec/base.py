from enum import IntEnum, Enum
import sys
sys.path.insert(0, '../')
from pygeminirec.recordlinks import RecordLinks
from pygeminirec.recordlinks import Result


class BaseExecutor:

    cads = RecordLinks()
    cars = RecordLinks()


    # update_all_cad_states - processes the command on itself as well as all chile CADs
    # process_all_cad_directives - does not process on itself because it is only called form an Apply
    #                         it processes CADs only
    # update_all_car_states - does not process on itself because it is only called from a CAD 
    #                         it processes on CARs only

    async def update_all_cad_states(self, **kwargs):
        print(f"Update CAD States top {self.prefix}")
        result, ret_mess = await self.set_state(**kwargs)

        if result == Result.SUCCESS:
            return await self.cads.execute_on_all('set_state', **kwargs)
        else:
            return result, ret_mess, self
    
    async def process_all_cad_directives(self, **kwargs):
        print(f"Process CAD Directives top {self.prefix}")
        return await self.cads.execute_on_all('process_directive', **kwargs)
        
    async def update_all_car_states(self, **kwargs):
        print(f"Updating CARs for {self.prefix}")
        return await self.cars.execute_on_all('set_state', **kwargs)


    async def set_state(self, **kwargs):
        print("Setting state ", kwargs)
        return True, "Set State"

    async def process_directive(self, **kwargs):
        print("Setting state ", kwargs)
        return True, "Set State"
    


class CARState:
    IDLE = "IDLE"
    PAUSED = "PAUSED"
    BUSY = "BUSY"
    ERR = "ERR"


class CADDirective:
    MARK = "MARK"
    STOP = "STOP"
    CLEAR = "CLEAR"
    START = "START"
    PRESET = "PRESET"
