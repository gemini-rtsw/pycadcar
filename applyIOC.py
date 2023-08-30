import caproto
from caproto.server import pvproperty, SubGroup, PVGroup, ioc_arg_parser, run
from applyrecord import applyRecord
from cadrecord import cadRecord



class MyIOC(PVGroup):
    applyRecord = SubGroup(applyRecord, prefix='apply.')
    cadRecord = SubGroup(cadRecord, prefix='applyC.')


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='tgnirs:dc:',
        desc="Run an IOC with a simple record."
    )
    ioc = MyIOC(**ioc_options)

    run(ioc.pvdb, **run_options)


