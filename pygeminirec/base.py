from enum import IntEnum, Enum
import sys
sys.path.insert(0, '../')
from pygeminirec.recordlinks import RecordLinks


class BaseExecutor:

    def __init__(self):
        self.cads = RecordLinks()
        self.cars = RecordLinks()


    # update_all_cad_states - processes the command on itself as well as all chile CADs
    # process_all_cad_directives - does not process on itself because it is only called form an Apply
    #                         it processes CADs only
    # update_all_car_states - does not process on itself because it is only called from a CAD 
    #                         it processes on CARs only

    async def update_all_cad_states(self, reverse, **kwargs):
        print(f"Update CAD States top {self.prefix}")
        result = await self.set_state(**kwargs)

        return await self.cads.execute_on_all('cads', 'set_state', reverse, **kwargs)

    
    async def process_all_cad_directives(self, reverse, **kwargs):
        print(f"Process CAD Directives top {self.prefix}")
        return await self.cads.execute_on_all('cads', 'process_directive', reverse, **kwargs)
        
    async def update_all_car_states(self, reverse, **kwargs):
        print(f"Updating CARs for {self.prefix}")
        return await self.cars.execute_on_all('cars', 'set_state', reverse, **kwargs)


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
