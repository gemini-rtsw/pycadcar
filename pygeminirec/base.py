from enum import IntEnum, Enum
import sys
sys.path.insert(0, '../')
from pygeminirec.recordlinks import RecordLinks
from pygeminirec.recordlinks import debug_print



class BaseExecutor:

    def __init__(self):
        self.cads = RecordLinks()
        self.cars = RecordLinks()
        self.idle_override = False  # not idle override is used to create an abort cad
                                    # cads are block from executing until all directive are complete aka idle
                                    # an abort cad needs to execute while a directive is still busy in order to abort it


    def set_idle_override(self, val):
        self.idle_override = val

    # update_all_cad_states - processes the command on itself as well as all chile CADs
    # process_all_cad_directives - does not process on itself because it is only called form an Apply
    #                         it processes CADs only
    # update_all_car_states - does not process on itself because it is only called from a CAD 
    #                         it processes on CARs only

    async def update_all_cad_states(self, reverse, **kwargs):
        debug_print(f"Update CAD States top {self.prefix}")
        result = await self.set_state(**kwargs)

        return await self.cads.execute_on_all('cads', 'set_state', reverse, **kwargs)

    
    async def process_all_cad_directives(self, reverse, **kwargs):
        debug_print(f"Process CAD Directives top {self.prefix}")
        return await self.cads.execute_on_all('cads', 'process_cad_directive', reverse, **kwargs)
        
    async def update_all_car_states(self, reverse, **kwargs):
        debug_print(f"Updating CARs for {self.prefix}")
        return await self.cars.execute_on_all('cars', 'set_state', reverse, **kwargs)

    async def are_all_cars_idle(self, **kwargs):
        debug_print(f"Checking CARs for IDLE State")
        return await self.cars.execute_on_all('cars', 'is_idle', **kwargs)
    
    async def are_any_cads_idle_override(self, **kwargs):
        debug_print(f"Checking CADs for IDLE Override State")
        return not await self.cads.execute_on_all('cads', 'get_not_idle_override', **kwargs)
    
    async def set_state(self, **kwargs):
        debug_print("Setting State ", kwargs)
        return True

    async def process_directive(self, **kwargs):
        debug_print("Setting state ", kwargs)
        return True
    
    async def is_idle(self, **kwargs):
        debug_print("Get Is Idle ", kwargs)
        return True

    async def get_cad_by_name(self, name):
        return self.get_by_declaration_name(name)
    
    async def get_not_idle_override(self, **kwargs): # needs to be negated because execute_on_all will only break on False
        return not self.idle_override                # and we want to break on idle_override = True
    


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

