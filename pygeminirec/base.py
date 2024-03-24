from enum import IntEnum, Enum
import sys
sys.path.insert(0, '../')
from pygeminirec.recordlinks import RecordLinks


class BaseExecutor:

    cads = RecordLinks()
    cars = RecordLinks()


    async def update_cad_states(self, **kwargs):
        print(f"Update CAD States {self.prefix}")
        return await self.cads.execute_on_all(self.set_state, **kwargs)
    
    async def process_cad_directive(self, **kwargs):
        print(f"Process CAD Directives {self.prefix}")
        return await self.cads.execute_on_all(self.process_directive, **kwargs)

    async def update_car_states(self, **kwargs):
        print(f"Update CAR States {self.prefix}")
        return await self.cars.execute_on_all(self.set_state, **kwargs)


    async def set_state(self, **kwargs):
        print("Setting state ", kwargs)
        return True, "Set State"

    async def process_directive(self, **kwargs):
        print("Setting state ", kwargs)
        return True, "Set State"



class Result(IntEnum):
    ERROR = 0
    SUCCESS = 1

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
