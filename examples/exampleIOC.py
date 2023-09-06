import caproto
from caproto.server import pvproperty, SubGroup, PVGroup, ioc_arg_parser, run
from applyrecord import ApplyRecord
from cadrecord import CADRecord
from carrecord import CARRecord
import asyncio

#Run example as follows
# python exampleIOC.py --list-pvs
# caput exampleIOC:apply.DIR MARK


class CADTaskError(CADRecord):
    async def mark(self):
        print(f"{self.prefix} new mark - error")
        await self.setError("TEST ERROR")


class CADTask(CADRecord):
    async def stop(self):
        print(f"{self.prefix} new stop")

    async def clear(self):
        print(f"{self.prefix} new clear")

    async def preset(self):
        print(f"{self.prefix} new preset")
        print(f"{self.prefix} clear error")
        await self.clearError()

    async def start(self):
        print(f"{self.prefix} new start")


class MyIOC(PVGroup):

#Declare Records
    cadRecord1 = SubGroup(CADTask, prefix='applyC1.')
    cadRecord2 = SubGroup(CADTask, prefix='applyC2.')
    cadRecord3 = SubGroup(CADTaskError, prefix='applyC3.')
    cadRecord4 = SubGroup(CADTask, prefix='applyC4.')


    carRecord = SubGroup(CARRecord, prefix='applyCAR.')
    applyRecord = SubGroup(ApplyRecord, prefix='apply.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def sname_funct(self):
        print("SNAME processed")
        print("ERROR processing")
        self.cadRecord.VAL.write('ERROR')
        self.cadRecord.MESS.write("ERROR message")
        return None


    async def record_init(self):

        #Link CAD record to CAR record
        self.cadRecord1.car_record = self.carRecord

        #Link Apply record to CAD record
        self.applyRecord.cad_records = [self.cadRecord1, self.cadRecord2, self.cadRecord3, self.cadRecord4]

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='exampleIOC:',
        desc="Run an IOC with a simple record."
    )
    ioc = MyIOC(**ioc_options)

    # Initialize asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ioc.record_init())

    run(ioc.pvdb, **run_options)


