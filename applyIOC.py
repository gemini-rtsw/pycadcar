import caproto
from caproto.server import pvproperty, SubGroup, PVGroup, ioc_arg_parser, run
from applyrecord import ApplyRecord
from cadrecord import CADRecord
from carrecord import CARRecord
import asyncio

import sys
sys.path.append('/home/hawi.stecher/work/gnirsdc-lib')
import libgnirsioc

class MyIOC(PVGroup):


    cadRecord = SubGroup(CADRecord, prefix='applyC.')
    carRecord = SubGroup(CARRecord, prefix='applyCAR.')
    applyRecord = SubGroup(ApplyRecord, prefix='apply.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def sname_funct(self):
    	controller = libgnirsioc.controllerInterface()
    	return controller


    async def record_init(self):
        sname_ptr = self.sname_funct
        print("FUNCT PTR")

#lambda : controller = libgnirsioc.controllerInterface() 
        
        await self.cadRecord.setSNAM(sname_ptr)
        self.cadRecord.car_record = self.carRecord
        self.applyRecord.cad_records = [self.cadRecord]

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='tgnirs:dc:',
        desc="Run an IOC with a simple record."
    )
    ioc = MyIOC(**ioc_options)

    # Initialize asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ioc.record_init())

    run(ioc.pvdb, **run_options)


